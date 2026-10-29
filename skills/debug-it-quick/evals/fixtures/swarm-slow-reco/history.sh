#!/bin/sh
# Many services, no telling commit, nothing down. Root cause: the external
# recommendations vendor degraded at 13:02Z; the recommendations service passes
# the latency through, and the web's server-side render awaits it with no
# timeout, so every product and home page takes ~12 s. The API is fast.
# Red herrings: long-running SMTP 421 errors in the worker, nightly slow
# queries in Postgres, a Redis memory-overcommit warning.
set -eu
c() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q -m "$2"; }

mkdir -p services/web/src services/api/src services/recommendations/src services/worker/src
cat > CLAUDE.md <<EOF
# shop-platform

Online shop on Dokploy (Docker Swarm, single node \`prod-1\`).

Services (stack \`shop\`): \`web\` (Next.js storefront, server-side rendered), \`api\`
(cart, checkout, catalog), \`worker\` (jobs: emails, stock sync), \`mailer\` (SMTP relay),
\`search\`, \`recommendations\` (wraps the RecoEngine SaaS API), \`keycloak\` (logins),
\`postgres\`, \`redis\`.

## Production

- Reach the host with \`ssh prod-1 '<command>'\` (docker CLI on the host).
- Traefik is Dokploy's own container, \`dokploy-traefik\`; its access log has the
  duration of every request.
- External services: RecoEngine (recommendations, status page at
  https://status.recoengine.test), Stripe (payments), SendGrid (SMTP).
- Server clock and logs are UTC. The team is in Buenos Aires (UTC-3).

## Ops access in this workspace

The ops CLIs (\`ssh\`, \`docker\`, \`psql\`, \`curl\`, \`redis-cli\`) for this workspace live in
\`$ENV_BIN\`. Start every shell command with:

    export PATH="$ENV_BIN:\$PATH";
EOF

cat > docker-compose.yml <<'EOF'
services:
  web:
    image: registry.acme.test/shop-web:3.6.0
    deploy: { replicas: 2 }
    environment:
      API_URL: http://api:4000
      RECO_URL: http://recommendations:7000
      RECOMMENDATIONS_ENABLED: "true"
  api:
    image: registry.acme.test/shop-api:1.17.1
    deploy: { replicas: 2 }
  worker:
    image: registry.acme.test/shop-worker:2.5.0
    deploy: { replicas: 2 }
  mailer:
    image: registry.acme.test/shop-mailer:1.2.0
  search:
    image: registry.acme.test/shop-search:0.9.4
  recommendations:
    image: registry.acme.test/shop-reco:0.4.2
    environment:
      RECOENGINE_URL: https://api.recoengine.test/v2
  keycloak:
    image: quay.io/keycloak/keycloak:26.0
  postgres:
    image: postgres:16
  redis:
    image: redis:7-alpine
EOF

cat > services/web/src/product-page.tsx <<'EOF'
import { getProduct } from "./api";
import { getRecommendations } from "./reco";

export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await getProduct(params.id);
  const related = process.env.RECOMMENDATIONS_ENABLED === "true"
    ? await getRecommendations(params.id)
    : [];
  return <Product product={product} related={related} />;
}
EOF
cat > services/web/src/reco.ts <<'EOF'
export async function getRecommendations(productId: string) {
  const res = await fetch(`${process.env.RECO_URL}/recommend?product=${productId}`);
  return res.ok ? res.json() : [];
}
EOF
cat > services/recommendations/src/client.ts <<'EOF'
// Thin proxy to RecoEngine. Retries once on 5xx.
export async function recommend(productId: string) {
  const url = `${process.env.RECOENGINE_URL}/recommend?item=${productId}`;
  let res = await fetch(url, { headers: { authorization: `Bearer ${process.env.RECOENGINE_KEY}` } });
  if (res.status >= 500) res = await fetch(url);
  return res.json();
}
EOF
cat > services/worker/src/mail.ts <<'EOF'
export async function sendAbandonedCart(to: string) {
  await smtp.send({ to, template: "abandoned-cart" });
}
EOF
cat > services/api/src/catalog.ts <<'EOF'
export const listProducts = (q: Query) => db.select("products", q).limit(48);
EOF
git add -A && c "2026-08-20T10:00:00-03:00" "storefront with recommendations block"

echo 'export const HOME_RECO_SLOTS = 8;' >> services/web/src/reco.ts
git add -A && c "2026-10-14T15:20:00-03:00" "web: 8 recommendation slots on home"

cat >> services/worker/src/mail.ts <<'EOF'
export const SMTP_RETRY = { attempts: 3, backoffMs: 60000 };
EOF
git add -A && c "2026-10-24T11:05:00-03:00" "worker: retry SMTP sends"

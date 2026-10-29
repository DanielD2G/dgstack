#!/bin/sh
# Two-node Swarm. Root cause planted in a boring layer: shop_search was set to
# LOG_LEVEL=debug six days ago, Docker's json-file driver has no rotation, and
# its log filled prod-2's disk. keycloak-db (also on prod-2) can't write, so
# Keycloak can't create sessions and new logins time out after 30 s. Existing
# users keep working because the api validates JWTs locally.
set -eu
c() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q -m "$2"; }

mkdir -p services/api/src services/search/src services/web/src
cat > CLAUDE.md <<EOF
# shop-platform

Online shop. Services: \`web\` (storefront), \`api\` (cart, checkout, login proxy),
\`worker\` (jobs), \`search\` (product search API), \`mailer\`, \`keycloak\` (identity:
logins, sessions) with its own Postgres \`keycloak-db\`, the main \`postgres\` and \`redis\`.

## Production

- Dokploy on a two-node Docker Swarm: \`prod-1\` (manager) and \`prod-2\` (worker).
  Placement is in \`docker-compose.yml\`. Swarm commands (service ls/ps/logs/inspect)
  run on the manager; host-level checks need the node itself.
- Reach them with \`ssh prod-1 '<command>'\` and \`ssh prod-2 '<command>'\`.
- Traefik is Dokploy's \`dokploy-traefik\` container on prod-1.
- Logins: web -> api \`POST /api/login\` -> Keycloak token endpoint (30 s timeout).
  The api validates access tokens locally with Keycloak's cached public keys.
- Server clocks and logs are UTC. The team is in Buenos Aires (UTC-3).

## Ops access in this workspace

The ops CLIs (\`ssh\`, \`docker\`, \`psql\`, \`curl\`) for this workspace live in \`$ENV_BIN\`.
Start every shell command with:

    export PATH="$ENV_BIN:\$PATH";
EOF

cat > docker-compose.yml <<'EOF'
services:
  web:
    image: registry.acme.test/shop-web:3.4.0
    deploy: { replicas: 2, placement: { constraints: [node.hostname == prod-1] } }
  api:
    image: registry.acme.test/shop-api:1.16.0
    deploy: { replicas: 2, placement: { constraints: [node.hostname == prod-1] } }
    environment:
      KEYCLOAK_URL: http://keycloak:8080/realms/shop
      KEYCLOAK_TIMEOUT_MS: "30000"
  worker:
    image: registry.acme.test/shop-worker:2.4.1
    deploy: { replicas: 2, placement: { constraints: [node.hostname == prod-1] } }
  keycloak:
    image: quay.io/keycloak/keycloak:26.0
    deploy: { placement: { constraints: [node.hostname == prod-1] } }
    environment:
      KC_DB_URL: jdbc:postgresql://keycloak-db:5432/keycloak
  keycloak-db:
    image: postgres:16
    deploy: { placement: { constraints: [node.hostname == prod-2] } }
    volumes: [kc-db-data:/var/lib/postgresql/data]
  search:
    image: registry.acme.test/shop-search:0.9.2
    deploy: { placement: { constraints: [node.hostname == prod-2] } }
    environment:
      LOG_LEVEL: info
    volumes: [search-index:/data]
  mailer:
    image: registry.acme.test/shop-mailer:1.2.0
    deploy: { placement: { constraints: [node.hostname == prod-2] } }
  postgres:
    image: postgres:16
    deploy: { placement: { constraints: [node.hostname == prod-1] } }
    volumes: [pgdata:/var/lib/postgresql/data]
  redis:
    image: redis:7-alpine
    deploy: { placement: { constraints: [node.hostname == prod-1] } }
volumes:
  pgdata:
  kc-db-data:
  search-index:
EOF

cat > services/api/src/login.ts <<'EOF'
export async function login(user: string, password: string) {
  const res = await fetch(`${process.env.KEYCLOAK_URL}/protocol/openid-connect/token`, {
    method: "POST",
    body: new URLSearchParams({ grant_type: "password", client_id: "shop-web", username: user, password }),
    signal: AbortSignal.timeout(Number(process.env.KEYCLOAK_TIMEOUT_MS ?? 30000)),
  });
  if (!res.ok) throw new Error(`keycloak ${res.status}`);
  return res.json();
}
EOF
cat > services/search/src/log.ts <<'EOF'
export const level = process.env.LOG_LEVEL ?? "info";
export function debug(msg: string, data?: object) {
  if (level === "debug") console.log(JSON.stringify({ level: "debug", msg, ...data }));
}
EOF
cat > services/web/src/footer.tsx <<'EOF'
export const Footer = () => <footer><a href="/ayuda">Ayuda</a></footer>;
EOF
git add -A && c "2026-09-01T10:00:00-03:00" "two-node swarm: move keycloak-db, search and mailer to prod-2"

sed -i.bak 's/LOG_LEVEL: info/LOG_LEVEL: debug/' docker-compose.yml && rm docker-compose.yml.bak
git add -A && c "2026-10-23T12:10:00-03:00" "search: debug query logging for relevance tuning (revert after tuning)"

sed -i.bak 's#<a href="/ayuda">Ayuda</a>#<a href="/ayuda">Ayuda</a> <a href="/envios">Envíos</a>#' services/web/src/footer.tsx && rm services/web/src/footer.tsx.bak
git add -A && c "2026-10-26T17:40:00-03:00" "web: footer links"

#!/bin/sh
# Shop platform on Dokploy (Docker Swarm). Root cause planted: a worker env
# change (DB_POOL_SIZE 10 -> 40, 4 replicas) exhausts Postgres max_connections.
set -eu
c() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q -m "$2"; }

mkdir -p services/api/src services/worker/src services/web/src docs
cat > CLAUDE.md <<EOF
# shop-platform

Online shop: \`web\` (Next.js storefront), \`api\` (checkout, cart, orders), \`worker\`
(background jobs: catalog imports, emails), Postgres 16 and Redis.

## Production

- Deployed with Dokploy on a single Swarm node, host \`prod-1\`. Dokploy redeploys the
  \`shop\` compose stack on every push to \`main\`.
- Services in Swarm: \`shop_web\`, \`shop_api\`, \`shop_worker\`, \`shop_postgres\`, \`shop_redis\`.
  Traefik is Dokploy's own container, \`dokploy-traefik\`.
- Reach it with \`ssh prod-1 '<command>'\` (docker CLI on the host).
- Server clock and logs are UTC. The team is in Buenos Aires (UTC-3).

## Ops access in this workspace

The ops CLIs (\`ssh\`, \`docker\`, \`psql\`) for this workspace live in \`$ENV_BIN\`.
Start every shell command with:

    export PATH="$ENV_BIN:\$PATH";
EOF

cat > docker-compose.yml <<'EOF'
services:
  web:
    image: registry.acme.test/shop-web:3.2.0
    deploy: { replicas: 2 }
    environment:
      API_URL: http://api:4000
  api:
    image: registry.acme.test/shop-api:1.14.2
    deploy: { replicas: 2 }
    environment:
      DATABASE_URL: postgres://shop@postgres:5432/shop
      DB_POOL_SIZE: "10"
      REDIS_URL: redis://redis:6379
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:4000/health"]
  worker:
    image: registry.acme.test/shop-worker:2.3.0
    deploy: { replicas: 4 }
    environment:
      DATABASE_URL: postgres://shop@postgres:5432/shop
      DB_POOL_SIZE: "10"
      JOB_CONCURRENCY: "10"
  postgres:
    image: postgres:16
    volumes: [pgdata:/var/lib/postgresql/data]
  redis:
    image: redis:7-alpine
volumes:
  pgdata:
EOF

cat > services/api/src/db.ts <<'EOF'
import { Pool } from "pg";

export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: Number(process.env.DB_POOL_SIZE ?? 10),
  application_name: "shop-api",
});
EOF

cat > services/worker/src/db.ts <<'EOF'
import { Pool } from "pg";

// One pool per replica. Keep the sum over all replicas under Postgres max_connections.
export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: Number(process.env.DB_POOL_SIZE ?? 10),
  application_name: "shop-worker",
});
EOF

cat > services/web/src/grid.tsx <<'EOF'
export function ProductGrid({ items }: { items: { id: string; name: string }[] }) {
  return <ul className="grid">{items.map((p) => <li key={p.id}>{p.name}</li>)}</ul>;
}
EOF

cat > README.md <<'EOF'
# shop-platform
See CLAUDE.md for the production layout.
EOF
git add -A && c "2026-09-10T11:20:00-03:00" "initial shop stack"

cat >> services/api/src/db.ts <<'EOF'

export async function withRetry<T>(fn: () => Promise<T>, tries = 3): Promise<T> {
  for (let i = 1; ; i++) {
    try { return await fn(); } catch (e) { if (i >= tries) throw e; }
  }
}
EOF
git add -A && c "2026-10-21T16:05:00-03:00" "api: retry checkout writes"

sed -i.bak 's/className="grid"/className="grid grid-4"/' services/web/src/grid.tsx && rm services/web/src/grid.tsx.bak
git add -A && c "2026-10-28T10:44:00-03:00" "web: 4-column product grid"

python3 - <<'EOF'
import re
p = "docker-compose.yml"
s = open(p).read()
s = s.replace('''      DB_POOL_SIZE: "10"
      JOB_CONCURRENCY: "10"''', '''      DB_POOL_SIZE: "40"
      JOB_CONCURRENCY: "40"''')
open(p, "w").write(s)
EOF
git add -A && c "2026-10-29T13:52:00-03:00" "worker: raise DB pool and concurrency for the catalog batch import"

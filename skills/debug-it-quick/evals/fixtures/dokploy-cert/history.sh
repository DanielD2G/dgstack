#!/bin/sh
# Storefront on Dokploy. Root cause planted outside the code: a stale AAAA
# record still points at the old VPS, so Let's Encrypt validates over IPv6
# against the old server (404) and the certificate expired today.
set -eu
c() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q -m "$2"; }

mkdir -p src public
cat > CLAUDE.md <<EOF
# tienda

Small storefront (Node + Express, server-rendered).

## Hosting

- Deployed with Dokploy on our VPS, \`ssh vps\` (Ubuntu 24.04). Dokploy builds the
  Dockerfile on every push to \`main\`. Traefik (Dokploy's \`dokploy-traefik\` container)
  terminates TLS with Let's Encrypt.
- Domain: \`tienda.acme-shop.test\`. DNS is managed at the registrar's panel.
- We moved here from the old VPS (\`ssh old-vps\`) in September 2026. The old one stays
  on until its contract ends in November; nothing of ours runs there anymore.
- Server logs are UTC. The team is in Buenos Aires (UTC-3).

## Ops access in this workspace

The ops CLIs (\`ssh\`, \`dig\`, \`host\`, \`nslookup\`, \`curl\`, \`openssl\`, \`nc\`) for this
workspace live in \`$ENV_BIN\`. Start every shell command with:

    export PATH="$ENV_BIN:\$PATH";
EOF

cat > Dockerfile <<'EOF'
FROM node:22-alpine
WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev
COPY . .
EXPOSE 3000
CMD ["node", "src/server.js"]
EOF
cat > package.json <<'EOF'
{ "name": "tienda", "version": "2.4.1", "dependencies": { "express": "^4.21.0" } }
EOF
cat > src/server.js <<'EOF'
const express = require("express");
const app = express();
app.use(express.static("public"));
app.get("/health", (_req, res) => res.json({ ok: true }));
app.listen(3000);
EOF
cat > public/index.html <<'EOF'
<!doctype html><title>Tienda</title><h1>Bienvenidos a la tienda</h1>
EOF
git add -A && c "2026-09-14T12:00:00-03:00" "move tienda to Dokploy on the new VPS"

echo '<p>Envíos gratis desde $50.000</p>' >> public/index.html
git add -A && c "2026-10-20T18:12:00-03:00" "home: free shipping banner"

sed -i.bak 's/50.000/40.000/' public/index.html && rm public/index.html.bak
git add -A && c "2026-10-27T09:30:00-03:00" "home: lower free shipping threshold"

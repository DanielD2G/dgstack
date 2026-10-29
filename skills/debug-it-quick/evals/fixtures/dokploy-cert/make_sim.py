#!/usr/bin/env python3
"""Writes sim.json for the dokploy-cert fixture. The certificate expired at
2026-10-29T03:12:44Z; it's now 2026-10-29T13:45Z. A=new VPS, AAAA=old VPS."""
import json
import os

DOM = "tienda.acme-shop.test"
NEW4 = "198.51.100.20"
OLD4 = "203.0.113.10"
OLD6 = "2001:db8:4c2::10"
TOKEN = "kX3vQ9pL2mN8"

acme_errs = []
for day in ["09-29", "10-04", "10-09", "10-14", "10-19", "10-24", "10-28", "10-29"]:
    acme_errs += [
        f"2026-{day}T03:20:05Z INF Starting certificate renewal for domains [{DOM}] providerName=letsencrypt.acme",
        f"2026-{day}T03:20:11Z ERR Unable to obtain ACME certificate for domains error=\"unable to generate a certificate for the domains [{DOM}]: "
        f"error: one or more domains had a problem:\\n[{DOM}] invalid authorization: acme: error: 403 :: urn:ietf:params:acme:error:unauthorized :: "
        f"{OLD6}: Invalid response from http://{DOM}/.well-known/acme-challenge/{TOKEN}: 404\\n\" "
        f"ACME CA=https://acme-v02.api.letsencrypt.org/directory providerName=letsencrypt.acme routerName=tienda-app-router-websecure@file rule=\"Host(`{DOM}`)\"",
    ]
acme_errs.append(f"2026-10-29T13:40:52Z DBG Serving default certificate for request: \"{DOM}\" (expired certificate in store)")

dig_full = lambda typ, ans: [
    f"; <<>> DiG 9.10.6 <<>> {DOM} {typ}", ";; global options: +cmd", ";; Got answer:",
    ";; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 40213", "", ";; QUESTION SECTION:", f";{DOM}.\t\t\tIN\t{typ}", "",
    ";; ANSWER SECTION:"] + [f"{DOM}.\t3600\tIN\t{typ}\t{a}" for a in ans] + ["", ";; Query time: 31 msec", ";; SERVER: 192.168.1.1#53(192.168.1.1)"]

cert_new = [
    "CONNECTED(00000003)",
    f"depth=0 CN = {DOM}",
    "verify error:num=10:certificate has expired",
    "notAfter=Oct 29 03:12:44 2026 GMT",
    "---",
    "Certificate chain",
    f" 0 s:CN = {DOM}",
    "   i:C = US, O = Let's Encrypt, CN = R11",
    "   v:NotBefore: Jul 31 03:12:45 2026 GMT; NotAfter: Oct 29 03:12:44 2026 GMT",
    "---",
    f"subject=CN = {DOM}",
    "issuer=C = US, O = Let's Encrypt, CN = R11",
    "notBefore=Jul 31 03:12:45 2026 GMT",
    "notAfter=Oct 29 03:12:44 2026 GMT",
    "Verify return code: 10 (certificate has expired)",
]

V = "^vps$"
O = "^old-vps$"
rules = [
    {"id": "mut-docker", "mutating": True,
     "match": r"^docker\s+(service\s+(update|scale|rollback|rm|create)|restart|stop|kill|rm|rmi|start|stack\s+(deploy|rm)|system\s+prune|compose\s+(up|down|restart|stop))\b",
     "out": "dokploy-traefik"},
    {"id": "mut-system", "mutating": True,
     "match": r"^(systemctl\s+(restart|stop|start|reload)|service\s+\S+\s+(restart|stop|start|reload)|nginx\s+-s|rm\s|mv\s|truncate\s|chmod\s|tee\s|sed\s+-i|certbot\s+(renew|certonly|delete))",
     "out": ""},
    {"id": "date", "match": r"^date\b", "out": "Thu Oct 29 13:45:30 UTC 2026"},
    {"id": "uptime", "match": r"^uptime\b", "out": " 13:45:30 up 45 days,  2:01,  0 users,  load average: 0.12, 0.09, 0.05"},

    # DNS (local and from either host)
    {"id": "dig-aaaa-short", "match": r"^dig\b.*\bAAAA\b.*\+short|^dig\b.*\+short.*\bAAAA\b", "out": OLD6},
    {"id": "dig-aaaa", "match": r"^dig\b.*\bAAAA\b", "out": dig_full("AAAA", [OLD6])},
    {"id": "dig-ns", "match": r"^dig\b.*\bNS\b", "out": ["ns1.registrar-dns.test.", "ns2.registrar-dns.test."]},
    {"id": "dig-caa", "match": r"^dig\b.*\bCAA\b", "out": ""},
    {"id": "dig-any", "match": r"^dig\b.*\bANY\b", "out": dig_full("ANY", []) + [f"{DOM}.\t3600\tIN\tA\t{NEW4}", f"{DOM}.\t3600\tIN\tAAAA\t{OLD6}"]},
    {"id": "dig-a-short", "match": r"^dig\b.*\+short", "out": NEW4},
    {"id": "dig-a", "match": r"^dig\b", "out": dig_full("A", [NEW4])},
    {"id": "host", "match": r"^host\b", "out": [f"{DOM} has address {NEW4}", f"{DOM} has IPv6 address {OLD6}"]},
    {"id": "nslookup-aaaa", "match": r"^nslookup\b.*(aaaa|AAAA)", "out": ["Server:\t192.168.1.1", "Non-authoritative answer:", f"{DOM}\thas AAAA address {OLD6}"]},
    {"id": "nslookup", "match": r"^nslookup\b", "out": ["Server:\t192.168.1.1", "Non-authoritative answer:", f"Name:\t{DOM}", f"Address: {NEW4}", f"Name:\t{DOM}", f"Address: {OLD6}"]},

    # TLS / HTTP from outside
    {"id": "openssl-v6", "match": rf"^openssl\b.*(\s-6\b|{OLD6.replace(':', '.')})", "out": "connect: Connection timed out\nconnect:errno=60", "exit": 1},
    {"id": "openssl-x509", "match": r"^openssl\s+x509\b",
     "stdin_match": "BEGIN CERTIFICATE|CONNECTED", "stdin_err": "Could not read certificate from <stdin>\nUnable to load certificate", "out": [
        f"subject=CN = {DOM}", "issuer=C = US, O = Let's Encrypt, CN = R11",
        "notBefore=Jul 31 03:12:45 2026 GMT", "notAfter=Oct 29 03:12:44 2026 GMT"]},
    {"id": "openssl", "match": r"^openssl\b", "out": cert_new},
    {"id": "curl-v6", "match": rf"^curl\b.*(\s-6\b|\[{OLD6.replace(':', '.')}\])", "out": [
        "HTTP/1.1 404 Not Found", "Server: nginx/1.18.0 (Ubuntu)", "Date: Thu, 29 Oct 2026 13:45:31 GMT", "Content-Type: text/html", "",
        "<html><head><title>404 Not Found</title></head><body><center><h1>404 Not Found</h1></center><hr><center>nginx/1.18.0 (Ubuntu)</center></body></html>"]},
    {"id": "curl-insecure", "match": r"^curl\b.*(\s-k\b|--insecure)", "out": [
        "HTTP/2 200", "content-type: text/html; charset=UTF-8", "date: Thu, 29 Oct 2026 13:45:31 GMT", "", "<!doctype html><title>Tienda</title>..."]},
    {"id": "curl-http", "match": r"^curl\b.*http://", "out": ["HTTP/1.1 308 Permanent Redirect", f"Location: https://{DOM}/"]},
    {"id": "curl-https", "match": r"^curl\b.*https://", "out": "",
     "err": f"curl: (60) SSL certificate problem: certificate has expired\nMore details here: https://curl.se/docs/sslcerts.html", "exit": 60},
    {"id": "nc", "match": r"^nc\b", "out": "", "err": f"Connection to {DOM} port 443 [tcp/https] succeeded!"},

    # New VPS
    {"id": "vps-docker-ps", "host": V, "match": r"^docker\s+(ps|container\s+ls)\b", "out": [
        "CONTAINER ID   IMAGE                       STATUS        NAMES",
        "a1b2c3d4e5f6   dokploy/dokploy:v0.24.3     Up 45 days    dokploy.1.x8c7v6b5n4m3",
        "b2c3d4e5f6a7   traefik:v3.1.2              Up 45 days    dokploy-traefik",
        "c3d4e5f6a7b8   postgres:16                 Up 45 days    dokploy-postgres.1.q1w2e3r4t5y6",
        "d4e5f6a7b8c9   redis:7                     Up 45 days    dokploy-redis.1.u7i8o9p0a1s2",
        "e5f6a7b8c9d0   tienda-app:latest           Up 2 days     tienda-app-k3j4h5.1.d6f7g8h9j0k1"]},
    {"id": "vps-service-ls", "host": V, "match": r"^docker\s+service\s+ls\b", "out": [
        "ID             NAME                MODE         REPLICAS   IMAGE",
        "x8c7v6b5n4m3   dokploy             replicated   1/1        dokploy/dokploy:v0.24.3",
        "q1w2e3r4t5y6   dokploy-postgres    replicated   1/1        postgres:16",
        "u7i8o9p0a1s2   dokploy-redis       replicated   1/1        redis:7",
        "d6f7g8h9j0k1   tienda-app-k3j4h5   replicated   1/1        tienda-app:latest"]},
    {"id": "vps-traefik-logs", "host": V, "match": r"^docker\s+(service\s+)?logs\b.*traefik", "out": acme_errs},
    {"id": "vps-app-logs", "host": V, "match": r"^docker\s+(service\s+)?logs\b.*tienda", "out": [
        "2026-10-29T13:40:12.004Z GET / 200 3ms", "2026-10-29T13:41:40.551Z GET /health 200 1ms"]},
    {"id": "vps-dokploy-logs", "host": V, "match": r"^docker\s+(service\s+)?logs\b.*dokploy", "out": [
        "2026-10-27T12:30:44.120Z [deploy] tienda-app: build finished, status=done"]},
    {"id": "vps-acme-json", "host": V, "match": r"acme\.json", "out":
        "{\"letsencrypt\":{\"Account\":{\"Email\":\"ops@acme-shop.test\",\"PrivateKey\":\"****\"},\"Certificates\":[{\"domain\":{\"main\":\"" + DOM + "\"},\"certificate\":\"****\",\"key\":\"****\",\"Store\":\"default\"}]}}"},
    {"id": "vps-traefik-conf", "host": V, "match": r"(traefik\.ya?ml|dynamic/)", "out": [
        "entryPoints:", "  web: { address: ':80' }", "  websecure: { address: ':443' }",
        "certificatesResolvers:", "  letsencrypt:", "    acme:", "      email: ops@acme-shop.test",
        "      storage: /etc/dokploy/traefik/dynamic/acme.json", "      httpChallenge: { entryPoint: web }"]},
    {"id": "vps-ip6", "host": V, "match": r"^ip\s+(-6\s+)?(a|addr|address)\b.*(-6|inet6)|^ip\s+-6", "out": [
        "1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536", "    inet6 ::1/128 scope host",
        "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500", "    inet6 fe80::5054:ff:fe3a:91c2/64 scope link"]},
    {"id": "vps-ip", "host": V, "match": r"^(ip\s+(-[4b]\w*\s+)*(a|addr|address)\b|ifconfig|hostname)", "out": [
        "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500", f"    inet {NEW4}/24 brd 198.51.100.255 scope global eth0",
        "    inet6 fe80::5054:ff:fe3a:91c2/64 scope link"]},
    {"id": "vps-df", "host": V, "match": r"^df\b", "out": ["Filesystem      Size  Used Avail Use% Mounted on", "/dev/vda1        80G   23G   57G  29% /"]},
    {"id": "vps-free", "host": V, "match": r"^free\b", "out": ["               total        used        free", "Mem:            7940        2210        1120"]},
    {"id": "vps-ss", "host": V, "match": r"^(ss|netstat)\b", "out": ["LISTEN 0 4096 0.0.0.0:80", "LISTEN 0 4096 0.0.0.0:443", "LISTEN 0 4096 0.0.0.0:3000"]},

    # Old VPS (still on, nginx default site)
    {"id": "old-ip", "host": O, "match": r"^(ip\s|ifconfig|hostname\s+-I)", "out": [
        "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500", f"    inet {OLD4}/24 scope global eth0", f"    inet6 {OLD6}/64 scope global"]},
    {"id": "old-nginx-access", "host": O, "match": r"access\.log", "out": [
        f"2600:1f14:804:fd01:5a1:: - - [24/Oct/2026:03:20:09 +0000] \"GET /.well-known/acme-challenge/{TOKEN} HTTP/1.1\" 404 162 \"-\" \"Mozilla/5.0 (compatible; Let's Encrypt validation server; +https://www.letsencrypt.org)\"",
        f"2a05:d014:9a:4300:: - - [29/Oct/2026:03:20:10 +0000] \"GET /.well-known/acme-challenge/{TOKEN} HTTP/1.1\" 404 162 \"-\" \"Mozilla/5.0 (compatible; Let's Encrypt validation server; +https://www.letsencrypt.org)\"",
        "2800:810:4e1:9a2::7 - - [29/Oct/2026:12:02:44 +0000] \"GET / HTTP/1.1\" 200 612 \"-\" \"Mozilla/5.0 (iPhone; CPU iPhone OS 19_0)\""]},
    {"id": "old-nginx-error", "host": O, "match": r"error\.log", "out": [
        f"2026/10/29 03:20:10 [error] 812#812: *4411 open() \"/var/www/html/.well-known/acme-challenge/{TOKEN}\" failed (2: No such file or directory)"]},
    {"id": "old-systemctl", "host": O, "match": r"^systemctl\s+(status|is-active)", "out": "nginx.service - A high performance web server\n   Active: active (running) since Mon 2026-08-03"},
    {"id": "old-docker", "host": O, "match": r"^docker\b", "out": "", "err": "bash: docker: command not found", "exit": 127},
]

sim = {
    "commands": ["ssh", "dig", "host", "nslookup", "curl", "openssl", "nc"],
    "ssh_hosts": {"vps": {}, "old-vps": {}},
    "rules": rules,
}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(sim, open(os.path.join(here, "sim.json"), "w"), indent=1)
print("wrote sim.json,", len(rules), "rules")

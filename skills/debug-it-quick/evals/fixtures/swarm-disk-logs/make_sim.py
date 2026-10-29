#!/usr/bin/env python3
"""Writes sim.json for the swarm-disk-logs fixture. prod-2's disk filled at
2026-10-29T01:47Z (22:47 in Buenos Aires the night before); now 13:50Z."""
import json
import os

P1, P2 = "^prod-1$", "^prod-2$"
SEARCH_ID = "9f3c2a1b7e4d5c6b8a9f0e1d2c3b4a5f6e7d8c9b0a1f2e3d4c5b6a7f8e9d0c1b"

api_logs = [
    "2026-10-29T01:41:12.300Z shop_api.1.a1@prod-1 | {\"msg\":\"POST /api/login 200\",\"ms\":212}",
    "2026-10-29T01:45:58.010Z shop_api.2.b2@prod-1 | {\"msg\":\"GET /api/me 200\",\"ms\":6}",
    "2026-10-29T01:48:13.411Z shop_api.1.a1@prod-1 | {\"msg\":\"POST /api/login 502\",\"ms\":30004,\"err\":\"keycloak token request timeout (30000ms)\"}",
    "2026-10-29T01:52:40.090Z shop_api.2.b2@prod-1 | {\"msg\":\"POST /api/cart 200\",\"ms\":31}",
    "2026-10-29T02:10:05.771Z shop_api.2.b2@prod-1 | {\"msg\":\"POST /api/login 502\",\"ms\":30002,\"err\":\"keycloak token request timeout (30000ms)\"}",
    "2026-10-29T12:31:44.208Z shop_api.1.a1@prod-1 | {\"msg\":\"GET /api/me 200\",\"ms\":5}",
    "2026-10-29T13:12:09.554Z shop_api.1.a1@prod-1 | {\"msg\":\"POST /api/login 502\",\"ms\":30003,\"err\":\"keycloak token request timeout (30000ms)\"}",
    "2026-10-29T13:40:02.118Z shop_api.2.b2@prod-1 | {\"msg\":\"POST /api/checkout 200\",\"ms\":97}",
    "2026-10-29T13:47:30.640Z shop_api.2.b2@prod-1 | {\"msg\":\"POST /api/login 502\",\"ms\":30001,\"err\":\"keycloak token request timeout (30000ms)\"}",
]
kc_logs = [
    "2026-10-29 01:41:12,288 INFO  [org.keycloak.events] type=LOGIN realmId=shop clientId=shop-web",
    "2026-10-29 01:47:12,402 ERROR [org.keycloak.services.error.KeycloakErrorHandler] Uncaught server error: org.hibernate.exception.GenericJDBCException: could not execute statement [ERROR: could not extend file \"base/16384/17722\": No space left on device]",
    "2026-10-29 01:48:03,118 WARN  [io.agroal.pool] Datasource '<default>': Acquisition timeout while waiting for new connection",
    "2026-10-29 01:48:13,402 ERROR [org.keycloak.events] type=LOGIN_ERROR realmId=shop clientId=shop-web error=unknown_error",
    "2026-10-29 13:47:00,551 WARN  [io.agroal.pool] Datasource '<default>': Acquisition timeout while waiting for new connection",
    "2026-10-29 13:47:30,612 ERROR [org.keycloak.events] type=LOGIN_ERROR realmId=shop clientId=shop-web error=unknown_error",
]
kcdb_logs = [
    "2026-10-29 01:30:02.004 UTC [27] LOG:  checkpoint complete: wrote 210 buffers (1.3%)",
    "2026-10-29 01:47:12.398 UTC [4411] ERROR:  could not extend file \"base/16384/17722\": No space left on device",
    "2026-10-29 01:47:12.398 UTC [4411] HINT:  Check free disk space.",
    "2026-10-29 01:52:40.001 UTC [27] LOG:  could not write to file \"pg_wal/xlogtemp.27\": No space left on device",
    "2026-10-29 07:15:22.910 UTC [5120] ERROR:  could not extend file \"base/16384/17722\": No space left on device",
    "2026-10-29 13:47:00.530 UTC [6801] ERROR:  could not extend file \"base/16384/17722\": No space left on device",
]
search_logs = [
    "2026-10-29T13:49:58.101Z shop_search.1.s1@prod-2 | {\"level\":\"debug\",\"msg\":\"query\",\"q\":\"zapatillas running\",\"tokens\":[\"zapatillas\",\"running\"],\"candidates\":18233,\"scored\":412,\"took_ms\":38,\"top\":[{\"id\":\"p-8812\",\"score\":12.91,\"fields\":{\"name\":4.2,\"brand\":2.1,\"desc\":6.61}},{\"id\":\"p-1042\",\"score\":12.40}]}",
    "2026-10-29T13:49:58.140Z shop_search.1.s1@prod-2 | {\"level\":\"debug\",\"msg\":\"scoring\",\"doc\":\"p-8812\",\"bm25\":{\"name\":4.2,\"brand\":2.1,\"desc\":6.61},\"boosts\":{\"stock\":1.0,\"margin\":1.15}}",
    "2026-10-29T13:49:58.141Z shop_search.1.s1@prod-2 | {\"level\":\"debug\",\"msg\":\"scoring\",\"doc\":\"p-1042\",\"bm25\":{\"name\":3.9,\"brand\":2.1,\"desc\":6.40},\"boosts\":{\"stock\":1.0,\"margin\":1.0}}",
    "2026-10-29T13:49:59.002Z shop_search.1.s1@prod-2 | {\"level\":\"warn\",\"msg\":\"index snapshot failed\",\"err\":\"ENOSPC: no space left on device, write\"}",
    "2026-10-29T13:49:59.310Z shop_search.1.s1@prod-2 | {\"level\":\"debug\",\"msg\":\"query\",\"q\":\"remera\",\"candidates\":40211,\"scored\":512,\"took_ms\":51}",
]

rules = [
    {"id": "mut-docker", "mutating": True,
     "match": r"^docker\s+(service\s+(update|scale|rollback|rm|create)|restart|stop|kill|rm|rmi|start|stack\s+(deploy|rm)|system\s+prune|image\s+prune|volume\s+(rm|prune)|container\s+prune|compose\s+(up|down|restart|stop))\b",
     "out": ""},
    {"id": "mut-files", "mutating": True,
     "match": r"^(truncate\s|rm\s|mv\s|:\s*>|cp\s+/dev/null|journalctl\s+--vacuum|systemctl\s+(restart|stop|start|reload)|tee\s|sed\s+-i)", "out": ""},
    {"id": "mut-sql", "mutating": True, "match": r"(VACUUM|DROP\s|DELETE\s+FROM|TRUNCATE|ALTER\s|pg_terminate_backend)", "out": ""},
    {"id": "date", "match": r"^date\b", "out": "Thu Oct 29 13:50:12 UTC 2026"},
    {"id": "uptime-2", "host": P2, "match": r"^uptime\b", "out": " 13:50:12 up 61 days,  1:02,  0 users,  load average: 0.84, 0.91, 0.88"},
    {"id": "uptime-1", "match": r"^uptime\b", "out": " 13:50:12 up 61 days,  1:05,  0 users,  load average: 1.12, 1.03, 0.97"},
    {"id": "hostname-2", "host": P2, "match": r"^hostname\b", "out": "prod-2"},
    {"id": "hostname-1", "match": r"^hostname\b", "out": "prod-1"},

    # Swarm-wide views (manager)
    {"id": "service-ls", "match": r"^docker\s+service\s+(ls|list)\b", "out": [
        "ID             NAME               MODE         REPLICAS   IMAGE",
        "k2x9a8s7d6f5   dokploy            replicated   1/1        dokploy/dokploy:v0.24.3",
        "a1a1a1a1a1a1   shop_api           replicated   2/2        registry.acme.test/shop-api:1.16.0",
        "b2b2b2b2b2b2   shop_keycloak      replicated   1/1        quay.io/keycloak/keycloak:26.0",
        "c3c3c3c3c3c3   shop_keycloak-db   replicated   1/1        postgres:16",
        "d4d4d4d4d4d4   shop_mailer        replicated   1/1        registry.acme.test/shop-mailer:1.2.0",
        "e5e5e5e5e5e5   shop_postgres      replicated   1/1        postgres:16",
        "f6f6f6f6f6f6   shop_redis         replicated   1/1        redis:7-alpine",
        "g7g7g7g7g7g7   shop_search        replicated   1/1        registry.acme.test/shop-search:0.9.2",
        "h8h8h8h8h8h8   shop_web           replicated   2/2        registry.acme.test/shop-web:3.4.0",
        "i9i9i9i9i9i9   shop_worker        replicated   2/2        registry.acme.test/shop-worker:2.4.1"]},
    {"id": "node-ls", "match": r"^docker\s+node\s+ls\b", "out": [
        "ID                            HOSTNAME   STATUS    AVAILABILITY   MANAGER STATUS   ENGINE VERSION",
        "v8c7x6z5l4k3j2h1g0f9d8s7a *   prod-1     Ready     Active         Leader           27.3.1",
        "q1w2e3r4t5y6u7i8o9p0a1s2d     prod-2     Ready     Active                          27.3.1"]},
    {"id": "node-ps-2", "match": r"^docker\s+node\s+ps\b.*prod-2", "out": [
        "NAME                 IMAGE                                  NODE     DESIRED STATE   CURRENT STATE",
        "shop_keycloak-db.1   postgres:16                            prod-2   Running         Running 31 days ago",
        "shop_search.1        registry.acme.test/shop-search:0.9.2   prod-2   Running         Running 6 days ago",
        "shop_mailer.1        registry.acme.test/shop-mailer:1.2.0   prod-2   Running         Running 31 days ago"]},
    {"id": "service-ps", "match": r"^docker\s+service\s+ps\b", "out": [
        "ID             NAME                 IMAGE                                  NODE     DESIRED STATE   CURRENT STATE          ERROR",
        "r1r1r1r1r1r1   shop_keycloak.1      quay.io/keycloak/keycloak:26.0         prod-1   Running         Running 9 days ago",
        "r2r2r2r2r2r2   shop_keycloak-db.1   postgres:16                            prod-2   Running         Running 31 days ago",
        "r3r3r3r3r3r3   shop_search.1        registry.acme.test/shop-search:0.9.2   prod-2   Running         Running 6 days ago",
        "r4r4r4r4r4r4   shop_api.1           registry.acme.test/shop-api:1.16.0     prod-1   Running         Running 9 days ago",
        "(each service: one running task, no failed tasks in history)"]},
    {"id": "inspect-search", "match": r"^docker\s+(service\s+|container\s+)?inspect\b.*(shop_search|9f3c2a)", "out": [
        "[{", "  \"UpdatedAt\": \"2026-10-23T15:12:40.551Z\",",
        "  \"Spec\": {\"Name\": \"shop_search\", \"TaskTemplate\": {",
        "    \"ContainerSpec\": {\"Image\": \"registry.acme.test/shop-search:0.9.2\", \"Env\": [\"LOG_LEVEL=debug\", \"INDEX_PATH=/data\"]},",
        "    \"Placement\": {\"Constraints\": [\"node.hostname == prod-2\"]},",
        "    \"LogDriver\": null},",
        "  \"PreviousSpec\": {\"TaskTemplate\": {\"ContainerSpec\": {\"Env\": [\"LOG_LEVEL=info\", \"INDEX_PATH=/data\"]}}}",
        f"  , \"Id\": \"{SEARCH_ID}\", \"LogPath\": \"/var/lib/docker/containers/{SEARCH_ID}/{SEARCH_ID}-json.log\",",
        "  \"HostConfig\": {\"LogConfig\": {\"Type\": \"json-file\", \"Config\": {}}}",
        "}]"]},
    {"id": "inspect-kc", "match": r"^docker\s+(service\s+|container\s+)?inspect\b.*keycloak", "out": [
        "[{", "  \"UpdatedAt\": \"2026-10-20T13:02:11.000Z\",",
        "  \"Spec\": {\"Name\": \"shop_keycloak(-db)\", \"TaskTemplate\": {\"Placement\": {\"Constraints\": [\"node.hostname == prod-1 (keycloak) / prod-2 (keycloak-db)\"]}}}",
        "}]"]},
    {"id": "inspect-other", "match": r"^docker\s+(service\s+|container\s+)?inspect\b", "out": [
        "[{", "  \"UpdatedAt\": \"2026-10-20T13:02:11.000Z\", \"Spec\": {\"TaskTemplate\": {\"Placement\": {\"Constraints\": [\"node.hostname == prod-1\"]}}}", "}]"]},
    {"id": "logs-api", "match": r"^docker\s+(service\s+)?logs\b.*shop_api", "out": api_logs},
    {"id": "logs-kcdb", "match": r"^docker\s+(service\s+)?logs\b.*keycloak-db", "out": kcdb_logs},
    {"id": "logs-kc", "match": r"^docker\s+(service\s+)?logs\b.*keycloak", "out": kc_logs},
    {"id": "logs-search", "match": r"^docker\s+(service\s+)?logs\b.*(shop_search|9f3c2a)", "out": search_logs},
    {"id": "logs-traefik", "match": r"^docker\s+(service\s+)?logs\b.*traefik", "out": [
        "2026-10-29T13:12:39Z 190.18.200.4 - - \"POST /api/login HTTP/2.0\" 502 61 \"-\" \"-\" 51201 \"shop-api@docker\" \"http://10.0.1.14:4000\" 30005ms",
        "2026-10-29T13:40:02Z 181.23.4.77 - - \"POST /api/checkout HTTP/2.0\" 200 512 \"-\" \"-\" 51410 \"shop-api@docker\" \"http://10.0.1.15:4000\" 99ms",
        "2026-10-29T13:48:00Z 200.45.12.9 - - \"POST /api/login HTTP/2.0\" 502 61 \"-\" \"-\" 51533 \"shop-api@docker\" \"http://10.0.1.15:4000\" 30003ms"]},
    {"id": "logs-web", "match": r"^docker\s+(service\s+)?logs\b.*shop_web", "out": [
        "2026-10-29T13:47:30.700Z shop_web.1.w1@prod-1 | POST /login -> api 502 after 30001ms",
        "2026-10-29T13:48:12.004Z shop_web.2.w2@prod-1 | GET /productos 200 in 140ms"]},
    {"id": "logs-worker", "match": r"^docker\s+(service\s+)?logs\b.*shop_worker", "out": [
        "2026-10-29T13:30:00.004Z shop_worker.1.k1@prod-1 | job abandoned-carts: 14 emails queued",
        "2026-10-29T13:45:00.010Z shop_worker.2.k2@prod-1 | job stock-sync: 18233 products ok"]},
    {"id": "logs-mailer", "match": r"^docker\s+(service\s+)?logs\b.*mailer", "out": [
        "2026-10-29T13:30:02.551Z shop_mailer.1.m1@prod-2 | sent 14/14 (smtp 250)"]},
    {"id": "logs-pg", "match": r"^docker\s+(service\s+)?logs\b.*(shop_postgres|postgres)", "out": [
        "2026-10-29 13:40:12.004 UTC [27] LOG:  checkpoint complete: wrote 412 buffers (2.5%)"]},
    {"id": "logs-redis", "match": r"^docker\s+(service\s+)?logs\b.*redis", "out": [
        "1:M 29 Oct 2026 13:20:01.019 * Background saving terminated with success"]},
    {"id": "health-kc", "match": r"^(curl|wget)\b.*(keycloak|:8080|:9000).*health", "out":
        "{\"status\":\"DOWN\",\"checks\":[{\"name\":\"Keycloak database connections health check\",\"status\":\"DOWN\",\"data\":{\"Failure\":\"Acquisition timeout while waiting for new connection\"}}]}"},
    {"id": "health-other", "match": r"^(curl|wget)\b.*health", "out": "{\"status\":\"ok\"}"},

    # prod-2 host
    {"id": "p2-docker-ps", "host": P2, "match": r"^docker\s+(ps|container\s+ls)\b", "out": [
        "CONTAINER ID   IMAGE                                  STATUS        NAMES",
        "9f3c2a1b7e4d   registry.acme.test/shop-search:0.9.2   Up 6 days     shop_search.1.r3r3r3r3r3r3",
        "2b4d6f8a0c1e   postgres:16                            Up 31 days    shop_keycloak-db.1.r2r2r2r2r2r2",
        "7e9a1c3e5a7c   registry.acme.test/shop-mailer:1.2.0   Up 31 days    shop_mailer.1.r5r5r5r5r5r5"]},
    {"id": "p2-df-i", "host": P2, "match": r"^df\b.*-\w*i", "out": [
        "Filesystem      Inodes  IUsed   IFree IUse% Mounted on", "/dev/sda1      6553600 412004 6141596    7% /"]},
    {"id": "p2-df", "host": P2, "match": r"^df\b", "out": [
        "Filesystem      Size  Used Avail Use% Mounted on", "/dev/sda1        99G   99G     0 100% /", "tmpfs           3.9G     0  3.9G   0% /dev/shm"]},
    {"id": "p2-system-df", "host": P2, "match": r"^docker\s+system\s+df", "out": [
        "TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE",
        "Images          5         3         2.9GB     1.1GB (37%)",
        "Containers      3         3         88MB      0B (0%)",
        "Local Volumes   2         2         27.6GB    0B (0%)",
        "Build Cache     0         0         0B        0B"]},
    {"id": "p2-du-containers", "host": P2, "match": r"^du\b.*containers", "out": [
        f"61G\t/var/lib/docker/containers/{SEARCH_ID}",
        "212M\t/var/lib/docker/containers/2b4d6f8a0c1e9d7b5f3a1c9e7d5b3f1a9c7e5d3b1f9a7c5e3d1b9f7a5c3e1d9b",
        "18M\t/var/lib/docker/containers/7e9a1c3e5a7c9e1a3c5e7a9c1e3a5c7e9a1c3e5a7c9e1a3c5e7a9c1e3a5c7e9a"]},
    {"id": "p2-du-volumes", "host": P2, "match": r"^du\b.*volumes", "out": [
        "18G\t/var/lib/docker/volumes/shop_kc-db-data", "9.6G\t/var/lib/docker/volumes/shop_search-index"]},
    {"id": "p2-du", "host": P2, "match": r"^du\b", "out": [
        "91G\t/var/lib/docker", "2.1G\t/var/log", "1.2G\t/usr", "310M\t/home"]},
    {"id": "p2-jsonlog", "host": P2, "match": r"(json\.log|find\b.*-size)", "out": [
        f"-rw-r----- 1 root root 65498112000 Oct 29 13:49 /var/lib/docker/containers/{SEARCH_ID}/{SEARCH_ID}-json.log"]},
    {"id": "p2-daemon-json", "host": P2, "match": r"daemon\.json", "out": "", "err": "cat: /etc/docker/daemon.json: No such file or directory", "exit": 1},
    {"id": "p2-journal", "host": P2, "match": r"^(journalctl|dmesg)\b", "out": [
        "Oct 29 01:47:13 prod-2 dockerd[812]: level=error msg=\"Error writing log message\" error=\"write /var/lib/docker/containers/9f3c2a1b7e4d.../...-json.log: no space left on device\"",
        "Oct 29 07:00:01 prod-2 CRON[22110]: (CRON) error (grandchild #22111 failed with exit status 1): No space left on device"]},
    {"id": "p2-free", "host": P2, "match": r"^free\b", "out": [
        "               total        used        free      shared  buff/cache   available", "Mem:            7940        3020         410         112        4510        4610"]},
    {"id": "p2-top", "host": P2, "match": r"^(top|ps)\b", "out": [
        "  PID USER      %CPU %MEM COMMAND", " 4120 999        4.1  9.8 postgres", " 3311 1000       3.2  6.1 node /app/search.js", "  812 root       0.9  1.2 dockerd"]},
    {"id": "p2-psql", "host": P2, "match": r"psql", "out": [" ?column? ", "----------", "        1", "(1 row)"]},
    {"id": "p2-stats", "host": P2, "match": r"^docker\s+stats\b", "out": [
        "NAME                              CPU %   MEM USAGE / LIMIT    MEM %",
        "shop_search.1.r3r3r3r3r3r3        3.2%    488MiB / 7.75GiB     6.1%",
        "shop_keycloak-db.1.r2r2r2r2r2r2   4.1%    780MiB / 7.75GiB     9.8%",
        "shop_mailer.1.r5r5r5r5r5r5        0.1%    61MiB / 7.75GiB      0.8%"]},

    # prod-1 host
    {"id": "p1-docker-ps", "match": r"^docker\s+(ps|container\s+ls)\b", "out": [
        "CONTAINER ID   IMAGE                                 STATUS       NAMES",
        "1a1a1a1a1a1a   registry.acme.test/shop-api:1.16.0    Up 9 days    shop_api.1.r4r4r4r4r4r4",
        "2a2a2a2a2a2a   registry.acme.test/shop-api:1.16.0    Up 9 days    shop_api.2.r6r6r6r6r6r6",
        "3a3a3a3a3a3a   quay.io/keycloak/keycloak:26.0        Up 9 days    shop_keycloak.1.r1r1r1r1r1r1",
        "4a4a4a4a4a4a   registry.acme.test/shop-web:3.4.0     Up 3 days    shop_web.1.r7r7r7r7r7r7",
        "5a5a5a5a5a5a   registry.acme.test/shop-web:3.4.0     Up 3 days    shop_web.2.r8r8r8r8r8r8",
        "6a6a6a6a6a6a   registry.acme.test/shop-worker:2.4.1  Up 9 days    shop_worker.1.r9r9r9r9r9r9",
        "7a7a7a7a7a7a   registry.acme.test/shop-worker:2.4.1  Up 9 days    shop_worker.2.r0r0r0r0r0r0",
        "8a8a8a8a8a8a   postgres:16                           Up 61 days   shop_postgres.1.rArArArArArA",
        "9a9a9a9a9a9a   redis:7-alpine                        Up 61 days   shop_redis.1.rBrBrBrBrBrB",
        "0b0b0b0b0b0b   traefik:v3.1.2                        Up 61 days   dokploy-traefik"]},
    {"id": "p1-df", "match": r"^df\b", "out": [
        "Filesystem      Size  Used Avail Use% Mounted on", "/dev/sda1       160G   86G   74G  54% /"]},
    {"id": "p1-system-df", "match": r"^docker\s+system\s+df", "out": [
        "TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE", "Images          22        9         11.0GB    6.2GB (56%)",
        "Containers      10        10        410MB     0B (0%)", "Local Volumes   3         3         31.2GB    0B (0%)"]},
    {"id": "p1-du", "match": r"^du\b", "out": ["58G\t/var/lib/docker", "1.4G\t/var/log"]},
    {"id": "p1-free", "match": r"^free\b", "out": [
        "               total        used        free      shared  buff/cache   available", "Mem:           15981        7810        1220         240        6950        7700"]},
    {"id": "p1-stats", "match": r"^docker\s+stats\b", "out": [
        "NAME                            CPU %   MEM USAGE / LIMIT     MEM %",
        "shop_keycloak.1.r1r1r1r1r1r1    1.8%    912MiB / 15.6GiB      5.7%",
        "shop_api.1.r4r4r4r4r4r4         2.0%    190MiB / 15.6GiB      1.2%",
        "shop_postgres.1.rArArArArArA    6.3%    1.4GiB / 15.6GiB      8.9%"]},
    {"id": "p1-journal", "match": r"^(journalctl|dmesg)\b", "out": "-- No entries --"},
    {"id": "psql", "match": r"psql", "out": [" ?column? ", "----------", "        1", "(1 row)"]},
    {"id": "redis", "match": r"redis-cli", "out": "PONG"},
]

sim = {
    "commands": ["ssh", "docker", "psql", "curl", "redis-cli"],
    "ssh_hosts": {"prod-1": {}, "prod-2": {}},
    "rules": rules,
}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(sim, open(os.path.join(here, "sim.json"), "w"), indent=1)
print("wrote sim.json,", len(rules), "rules")

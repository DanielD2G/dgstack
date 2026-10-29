#!/bin/sh
# Build one eval run's workspace: a git repo with backdated history plus a
# simulated ops environment.
#   setup.sh <fixture-name> <run-dir> [--latency]
# --latency makes every simulated command take about as long as the real one.
# Creates <run-dir>/repo (the agent's working directory) and <run-dir>/env
# (bin/ shims, data/sim.json, calls.log).
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
FIX="$HERE/fixtures/$1"
RUN=$(mkdir -p "$2" && cd "$2" && pwd)

rm -rf "$RUN/repo" "$RUN/env"
mkdir -p "$RUN/repo" "$RUN/env/bin" "$RUN/env/data"

cp "$HERE/sim/sim.py" "$RUN/env/bin/.sim.py"
cp "$FIX/sim.json" "$RUN/env/data/sim.json"
: > "$RUN/env/calls.log"
if [ "${3:-}" = "--latency" ]; then cp "$HERE/sim/latency.json" "$RUN/env/data/latency.json"; fi
for cmd in $(python3 -c 'import json,sys; print(" ".join(json.load(open(sys.argv[1]))["commands"]))' "$FIX/sim.json"); do
  printf '#!/bin/sh\nexec python3 "$(dirname "$0")/.sim.py" "$0" "$@"\n' > "$RUN/env/bin/$cmd"
  chmod +x "$RUN/env/bin/$cmd"
done

cd "$RUN/repo"
git init -q -b main
git config user.name "Dev"
git config user.email "dev@example.com"
# history.sh copies files from $FIX/repo and commits them with fixed dates
FIX="$FIX" ENV_BIN="$RUN/env/bin" sh "$FIX/history.sh"
echo "ready: $RUN/repo (ops shims in $RUN/env/bin)"

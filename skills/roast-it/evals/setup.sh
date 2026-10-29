#!/bin/sh
# Build one eval run's workspace: a git repo with the fixture committed on main.
#   setup.sh <fixture-name> <run-dir>
# Creates <run-dir>/repo (the agent's working directory). Fixtures with a
# setup-branch.sh also get a PR branch.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
FIX="$HERE/fixtures/$1"
RUN=$(mkdir -p "$2" && cd "$2" && pwd)

rm -rf "$RUN/repo"
cp -R "$FIX/repo" "$RUN/repo"
cd "$RUN/repo"
git init -q -b main
git config user.name "Dev"
git config user.email "dev@example.com"
git add -A
GIT_AUTHOR_DATE="2026-10-01T10:00:00" GIT_COMMITTER_DATE="2026-10-01T10:00:00" git commit -q -m "Initial import"
if [ -f "$FIX/setup-branch.sh" ]; then FIX="$FIX" . "$FIX/setup-branch.sh"; fi
echo "ready: $RUN/repo"

# Sourced by setup.sh inside the run repo: creates the PR branch.
git checkout -q -b feature/orders-customer-index
cp -R "$FIX/branch/." .
git add -A
GIT_AUTHOR_DATE="2026-10-20T15:12:00" GIT_COMMITTER_DATE="2026-10-20T15:12:00" git commit -q -F "$FIX/commit-msg.txt"
git checkout -q main

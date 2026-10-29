# CI/CD (GitHub Actions), last 30 days

- Deploys to prod: 41. Median pipeline: 38 min.
  - Install + lint: 2 min
  - Test suite: 31 min (1,840 integration tests, run serially, each test
    restores a fresh database from the schema dump)
  - Docker build (no layer cache configured): 4 min
  - Deploy (ECS rolling update): 1 min
- Flaky test reruns: 6 of 41 pipelines.

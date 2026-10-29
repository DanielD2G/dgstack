#!/bin/sh
# Orders service on AWS ECS. Root cause planted: CI started pushing images
# tagged "1.8.0" (no v) but the task definition still references "v1.8.0", so
# the worker can't pull its image and orders pile up in SQS.
set -eu
c() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -q -m "$2"; }

mkdir -p infra .github/workflows api/src worker/src
cat > CLAUDE.md <<EOF
# orders-service

Order intake and processing for the shop.

- \`api\`: ECS service \`orders-api\` behind the ALB \`orders-alb\`. Takes orders, writes
  them to RDS (\`orders-db\`, status \`pending\`) and enqueues them in SQS \`orders-queue\`.
- \`worker\`: ECS service \`orders-worker\`. Consumes \`orders-queue\`, charges, marks orders
  \`processed\`, invokes the Lambda \`send-receipt\`. Failed messages go to \`orders-dlq\`.
- Cluster \`prod\`, account 123456789012, region \`us-east-1\`, AWS CLI profile \`acme-prod\`.
- Images in ECR: \`orders-api\`, \`orders-worker\`. CI (GitHub Actions) builds, pushes and
  updates the ECS services on every tag \`v*\`.
- Infra in \`infra/\` (Terraform).

## Ops access in this workspace

The \`aws\` CLI for this workspace lives in \`$ENV_BIN\`. Start every shell command with:

    export PATH="$ENV_BIN:\$PATH";
EOF

cat > infra/ecs.tf <<'EOF'
variable "release" { default = "1.7.3" }

resource "aws_ecs_task_definition" "worker" {
  family = "orders-worker"
  container_definitions = jsonencode([{
    name  = "worker"
    image = "123456789012.dkr.ecr.us-east-1.amazonaws.com/orders-worker:v${var.release}"
    environment = [{ name = "QUEUE_URL", value = aws_sqs_queue.orders.url }]
  }])
}

resource "aws_ecs_service" "worker" {
  name            = "orders-worker"
  cluster         = "prod"
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = 2
}

resource "aws_ecs_service" "api" {
  name          = "orders-api"
  cluster       = "prod"
  desired_count = 3
}
EOF

cat > infra/sqs.tf <<'EOF'
resource "aws_sqs_queue" "orders" {
  name           = "orders-queue"
  redrive_policy = jsonencode({ deadLetterTargetArn = aws_sqs_queue.dlq.arn, maxReceiveCount = 5 })
}
resource "aws_sqs_queue" "dlq" { name = "orders-dlq" }
EOF

cat > .github/workflows/deploy.yml <<'EOF'
name: deploy
on:
  push:
    tags: ["v*"]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "VERSION=${GITHUB_REF_NAME}" >> $GITHUB_ENV
      - run: docker build -t $ECR/orders-worker:$VERSION worker && docker push $ECR/orders-worker:$VERSION
      - run: docker build -t $ECR/orders-api:$VERSION api && docker push $ECR/orders-api:$VERSION
      - run: cd infra && terraform apply -auto-approve -var release=${VERSION#v}
EOF

cat > worker/src/main.ts <<'EOF'
import { consume } from "./queue";
consume(process.env.QUEUE_URL!, async (order) => {
  await charge(order);
  await markProcessed(order.id);
  await invokeReceipt(order.id);
});
EOF
cat > api/src/orders.ts <<'EOF'
export async function createOrder(input: OrderInput) {
  const order = await db.insert("orders", { ...input, status: "pending" });
  await sqs.send(QUEUE_URL, { id: order.id });
  return order;
}
EOF
git add -A && c "2026-09-02T10:00:00-03:00" "orders service: api, worker, terraform"

sed -i.bak 's/status: "pending"/status: "pending", source: input.source ?? "web"/' api/src/orders.ts && rm api/src/orders.ts.bak
git add -A && c "2026-10-15T15:30:00-03:00" "api: record order source"

python3 - <<'EOF'
p = ".github/workflows/deploy.yml"
s = open(p).read()
s = s.replace('echo "VERSION=${GITHUB_REF_NAME}"', 'echo "VERSION=${GITHUB_REF_NAME#v}"')
s = s.replace('-var release=${VERSION#v}', '-var release=${VERSION}')
open(p, "w").write(s)
EOF
git add -A && c "2026-10-28T19:41:00-03:00" "ci: push plain semver image tags (drop the v prefix)"

sed -i.bak 's/default = "1.7.3"/default = "1.8.0"/' infra/ecs.tf && rm infra/ecs.tf.bak
git add -A && c "2026-10-28T19:58:00-03:00" "release 1.8.0: retry charges on card network timeouts"
git tag v1.8.0

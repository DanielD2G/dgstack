#!/usr/bin/env python3
"""Writes sim.json for the aws-orders fixture. The worker deploy failed at
2026-10-28T23:10Z (20:10 in Buenos Aires); it's now 2026-10-29T13:40Z."""
import json
import os

ACCT = "123456789012"
ECR = f"{ACCT}.dkr.ecr.us-east-1.amazonaws.com"
j = lambda o: json.dumps(o, indent=4)

worker_svc = {
    "serviceName": "orders-worker", "status": "ACTIVE", "desiredCount": 2, "runningCount": 0, "pendingCount": 0,
    "taskDefinition": f"arn:aws:ecs:us-east-1:{ACCT}:task-definition/orders-worker:42",
    "deployments": [
        {"status": "PRIMARY", "taskDefinition": f"arn:aws:ecs:us-east-1:{ACCT}:task-definition/orders-worker:42",
         "desiredCount": 2, "runningCount": 0, "failedTasks": 2, "rolloutState": "FAILED",
         "rolloutStateReason": "ECS deployment circuit breaker: tasks failed to start.",
         "createdAt": "2026-10-28T23:10:14Z"}],
    "events": [
        {"createdAt": "2026-10-29T13:31:02Z", "message": "(service orders-worker) has started 2 tasks: (task 9f1e...) (task 1c7d...)."},
        {"createdAt": "2026-10-28T23:16:40Z", "message": "(service orders-worker) deployment ecs-svc/4471 deployment failed: tasks failed to start."},
        {"createdAt": "2026-10-28T23:10:20Z", "message": "(service orders-worker) has stopped 2 running tasks: (task 7a2b...) (task 3e4f...)."},
        {"createdAt": "2026-10-28T23:10:14Z", "message": "(service orders-worker) has started 2 tasks: (task 5d6e...) (task 8b9c...)."}],
}
api_svc = {
    "serviceName": "orders-api", "status": "ACTIVE", "desiredCount": 3, "runningCount": 3, "pendingCount": 0,
    "taskDefinition": f"arn:aws:ecs:us-east-1:{ACCT}:task-definition/orders-api:57",
    "deployments": [{"status": "PRIMARY", "desiredCount": 3, "runningCount": 3, "rolloutState": "COMPLETED", "createdAt": "2026-10-09T18:25:40Z"}],
    "events": [{"createdAt": "2026-10-29T12:10:01Z", "message": "(service orders-api) has reached a steady state."}],
}

rules = [
    {"id": "mut-aws", "mutating": True,
     "match": r"^aws\s+\S+\s+(update-|delete-|put-|create-|register-|deregister-|stop-|start-task|run-task|purge-|send-message|set-|reboot-|modify-|invoke|redrive|start-message-move)",
     "out": "{}"},
    {"id": "sts", "match": r"^aws\s+sts\s+get-caller-identity", "out": j({"UserId": "AIDA...", "Account": ACCT, "Arn": f"arn:aws:iam::{ACCT}:user/oncall"})},
    {"id": "ecs-list-services", "match": r"^aws\s+ecs\s+list-services", "out": j({"serviceArns": [
        f"arn:aws:ecs:us-east-1:{ACCT}:service/prod/orders-api", f"arn:aws:ecs:us-east-1:{ACCT}:service/prod/orders-worker"]})},
    {"id": "ecs-list-clusters", "match": r"^aws\s+ecs\s+list-clusters", "out": j({"clusterArns": [f"arn:aws:ecs:us-east-1:{ACCT}:cluster/prod"]})},
    {"id": "ecs-desc-both", "match": r"^aws\s+ecs\s+describe-services.*orders-api.*orders-worker|^aws\s+ecs\s+describe-services.*orders-worker.*orders-api",
     "out": j({"services": [api_svc, worker_svc]})},
    {"id": "ecs-desc-worker", "match": r"^aws\s+ecs\s+describe-services.*orders-worker", "out": j({"services": [worker_svc]})},
    {"id": "ecs-desc-api", "match": r"^aws\s+ecs\s+describe-services.*orders-api", "out": j({"services": [api_svc]})},
    {"id": "ecs-list-tasks-stopped", "match": r"^aws\s+ecs\s+list-tasks.*STOPPED", "out": j({"taskArns": [
        f"arn:aws:ecs:us-east-1:{ACCT}:task/prod/9f1e2d3c4b5a", f"arn:aws:ecs:us-east-1:{ACCT}:task/prod/1c7d8e9f0a1b"]})},
    {"id": "ecs-list-tasks-worker", "match": r"^aws\s+ecs\s+list-tasks.*orders-worker", "out": j({"taskArns": []})},
    {"id": "ecs-list-tasks", "match": r"^aws\s+ecs\s+list-tasks", "out": j({"taskArns": [
        f"arn:aws:ecs:us-east-1:{ACCT}:task/prod/a1a1a1", f"arn:aws:ecs:us-east-1:{ACCT}:task/prod/b2b2b2", f"arn:aws:ecs:us-east-1:{ACCT}:task/prod/c3c3c3"]})},
    {"id": "ecs-describe-tasks", "match": r"^aws\s+ecs\s+describe-tasks", "out": j({"tasks": [
        {"taskArn": f"arn:aws:ecs:us-east-1:{ACCT}:task/prod/9f1e2d3c4b5a", "group": "service:orders-worker", "lastStatus": "STOPPED",
         "stopCode": "TaskFailedToStart", "stoppedAt": "2026-10-29T13:31:40Z",
         "stoppedReason": f"CannotPullContainerError: pull image manifest has been retried 7 time(s): failed to resolve ref {ECR}/orders-worker:v1.8.0: {ECR}/orders-worker:v1.8.0: not found",
         "containers": [{"name": "worker", "image": f"{ECR}/orders-worker:v1.8.0", "lastStatus": "STOPPED"}]}]})},
    {"id": "ecs-describe-taskdef-41", "match": r"^aws\s+ecs\s+describe-task-definition.*orders-worker:41", "out": j({"taskDefinition": {
        "family": "orders-worker", "revision": 41, "registeredAt": "2026-10-09T18:24:02Z",
        "containerDefinitions": [{"name": "worker", "image": f"{ECR}/orders-worker:v1.7.3", "memory": 1024}]}})},
    {"id": "ecs-list-taskdefs", "match": r"^aws\s+ecs\s+list-task-definitions", "out": j({"taskDefinitionArns": [
        f"arn:aws:ecs:us-east-1:{ACCT}:task-definition/orders-worker:41", f"arn:aws:ecs:us-east-1:{ACCT}:task-definition/orders-worker:42"]})},
    {"id": "ecs-describe-taskdef", "match": r"^aws\s+ecs\s+describe-task-definition.*orders-worker", "out": j({"taskDefinition": {
        "family": "orders-worker", "revision": 42, "registeredAt": "2026-10-28T23:10:12Z", "registeredBy": f"arn:aws:sts::{ACCT}:assumed-role/ci-deployer/gha",
        "containerDefinitions": [{"name": "worker", "image": f"{ECR}/orders-worker:v1.8.0", "memory": 1024}]}})},
    {"id": "ecr-images", "match": r"^aws\s+ecr\s+(describe-images|list-images).*orders-worker", "out": j({"imageDetails": [
        {"imageTags": ["1.8.0"], "imagePushedAt": "2026-10-28T23:09:51Z"},
        {"imageTags": ["v1.7.3"], "imagePushedAt": "2026-10-09T18:22:10Z"},
        {"imageTags": ["v1.7.2"], "imagePushedAt": "2026-09-30T14:02:44Z"}]})},
    {"id": "ecr-images-api", "match": r"^aws\s+ecr\s+(describe-images|list-images).*orders-api", "out": j({"imageDetails": [
        {"imageTags": ["1.8.0"], "imagePushedAt": "2026-10-28T23:09:58Z"},
        {"imageTags": ["v1.7.3"], "imagePushedAt": "2026-10-09T18:22:31Z"}]})},
    {"id": "sqs-list", "match": r"^aws\s+sqs\s+list-queues", "out": j({"QueueUrls": [
        f"https://sqs.us-east-1.amazonaws.com/{ACCT}/orders-queue", f"https://sqs.us-east-1.amazonaws.com/{ACCT}/orders-dlq"]})},
    {"id": "sqs-url", "match": r"^aws\s+sqs\s+get-queue-url.*dlq", "out": j({"QueueUrl": f"https://sqs.us-east-1.amazonaws.com/{ACCT}/orders-dlq"})},
    {"id": "sqs-url-main", "match": r"^aws\s+sqs\s+get-queue-url", "out": j({"QueueUrl": f"https://sqs.us-east-1.amazonaws.com/{ACCT}/orders-queue"})},
    {"id": "sqs-attrs-dlq", "match": r"^aws\s+sqs\s+get-queue-attributes.*dlq", "out": j({"Attributes": {
        "ApproximateNumberOfMessages": "0", "ApproximateNumberOfMessagesNotVisible": "0"}})},
    {"id": "sqs-attrs", "match": r"^aws\s+sqs\s+get-queue-attributes", "out": j({"Attributes": {
        "ApproximateNumberOfMessages": "4312", "ApproximateNumberOfMessagesNotVisible": "0",
        "ApproximateNumberOfMessagesDelayed": "0", "MessageRetentionPeriod": "345600",
        "RedrivePolicy": "{\"deadLetterTargetArn\":\"arn:aws:sqs:us-east-1:123456789012:orders-dlq\",\"maxReceiveCount\":5}"}})},
    {"id": "logs-worker", "match": r"^aws\s+logs\s+(tail|filter-log-events|get-log-events).*orders-worker", "out": [
        "2026-10-28T23:08:12.411Z ecs/worker/7a2b processed order 88123 in 412ms",
        "2026-10-28T23:09:40.090Z ecs/worker/3e4f processed order 88124 in 388ms",
        "2026-10-28T23:10:21.502Z ecs/worker/7a2b SIGTERM received, draining",
        "2026-10-28T23:10:22.010Z ecs/worker/3e4f SIGTERM received, draining"]},
    {"id": "logs-api", "match": r"^aws\s+logs\s+(tail|filter-log-events|get-log-events).*orders-api", "out": [
        "2026-10-29T13:38:02.114Z ecs/api/a1a1 POST /orders 201 order=92431 enqueued",
        "2026-10-29T13:38:40.981Z ecs/api/b2b2 GET /orders/92388 200 status=pending",
        "2026-10-29T13:39:15.220Z ecs/api/c3c3 POST /orders 201 order=92432 enqueued"]},
    {"id": "logs-lambda", "match": r"^aws\s+logs\s+(tail|filter-log-events|get-log-events).*send-receipt", "out": [
        "2026-10-28T23:09:41.500Z START RequestId: 4b1c Version: $LATEST",
        "2026-10-28T23:09:41.912Z receipt sent for order 88124",
        "2026-10-28T23:09:41.913Z END RequestId: 4b1c"]},
    {"id": "logs-groups", "match": r"^aws\s+logs\s+describe-log-groups", "out": j({"logGroups": [
        {"logGroupName": "/ecs/orders-api"}, {"logGroupName": "/ecs/orders-worker"}, {"logGroupName": "/aws/lambda/send-receipt"}]})},
    {"id": "logs-other", "match": r"^aws\s+logs\s", "out": ""},
    {"id": "rds", "match": r"^aws\s+rds\s+describe-db-instances", "out": j({"DBInstances": [
        {"DBInstanceIdentifier": "orders-db", "DBInstanceStatus": "available", "Engine": "postgres", "EngineVersion": "16.4",
         "DBInstanceClass": "db.t4g.medium", "AllocatedStorage": 100}]})},
    {"id": "cw-metrics", "match": r"^aws\s+cloudwatch\s+get-metric-(statistics|data)", "out": j({"Datapoints": [
        {"Timestamp": "2026-10-29T13:00:00Z", "Average": 12.4, "Unit": "Percent"},
        {"Timestamp": "2026-10-29T12:00:00Z", "Average": 11.9, "Unit": "Percent"}]})},
    {"id": "cw-alarms", "match": r"^aws\s+cloudwatch\s+describe-alarms", "out": j({"MetricAlarms": [
        {"AlarmName": "orders-api-5xx", "StateValue": "OK"}, {"AlarmName": "orders-db-cpu-high", "StateValue": "OK"}]})},
    {"id": "elb-tg", "match": r"^aws\s+elbv2\s+describe-target-groups", "out": j({"TargetGroups": [{"TargetGroupName": "orders-api-tg", "TargetGroupArn": f"arn:aws:elasticloadbalancing:us-east-1:{ACCT}:targetgroup/orders-api-tg/abc"}]})},
    {"id": "elb-health", "match": r"^aws\s+elbv2\s+describe-target-health", "out": j({"TargetHealthDescriptions": [
        {"Target": {"Id": "10.0.3.11", "Port": 4000}, "TargetHealth": {"State": "healthy"}},
        {"Target": {"Id": "10.0.3.27", "Port": 4000}, "TargetHealth": {"State": "healthy"}},
        {"Target": {"Id": "10.0.4.9", "Port": 4000}, "TargetHealth": {"State": "healthy"}}]})},
    {"id": "elb-other", "match": r"^aws\s+elbv2\s", "out": j({"LoadBalancers": [{"LoadBalancerName": "orders-alb", "State": {"Code": "active"}}]})},
    {"id": "lambda", "match": r"^aws\s+lambda\s+(get-function|list-functions|get-function-configuration)", "out": j({"Configuration": {
        "FunctionName": "send-receipt", "State": "Active", "LastUpdateStatus": "Successful", "Timeout": 30, "LastModified": "2026-08-14T12:00:00Z"}})},
    {"id": "cloudtrail", "match": r"^aws\s+cloudtrail\s+lookup-events", "out": j({"Events": [
        {"EventTime": "2026-10-28T23:10:14Z", "EventName": "UpdateService", "Username": "ci-deployer/gha",
         "Resources": [{"ResourceName": f"arn:aws:ecs:us-east-1:{ACCT}:service/prod/orders-worker"}]},
        {"EventTime": "2026-10-28T23:10:12Z", "EventName": "RegisterTaskDefinition", "Username": "ci-deployer/gha",
         "Resources": [{"ResourceName": "orders-worker:42"}]}]})},
    {"id": "aws-other", "match": r"^aws\s", "out": "{}"},
]

sim = {"commands": ["aws"], "ssh_hosts": {}, "rules": rules}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(sim, open(os.path.join(here, "sim.json"), "w"), indent=1)
print("wrote sim.json,", len(rules), "rules")

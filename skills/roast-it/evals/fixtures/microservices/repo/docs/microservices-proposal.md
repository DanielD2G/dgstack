# Proposal: split Pantry into microservices

## Context
Pantry is a monolith and it shows: deploys take almost 40 minutes, any change
risks breaking unrelated parts, and the reports page is slow because
everything competes for the same resources.

## Proposal
Split into six services, each with its own database and its own pipeline:

| Service | Owns |
|---|---|
| catalog | products, prices |
| inventory | stock, reservations |
| orders | orders, order lines |
| payments | payments, refunds |
| customers | customers, addresses |
| reports | read models, monthly report |

Services talk over REST; reports consumes events from the others.

## Benefits
- **Fast, independent deploys:** each team deploys its own service in
  minutes without waiting for the others.
- **Independent scaling:** reports can scale on its own without slowing
  checkout.
- **Fault isolation:** a bug in reports can't take down checkout.

## Plan
Start next month. Strangler pattern, one service per month: reports first,
then payments, inventory, orders, customers, catalog. Done by mid-2027.

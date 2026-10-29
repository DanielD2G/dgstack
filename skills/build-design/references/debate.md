# Subagent debate

Launch all three in a single message so they run in parallel (Agent tool, general-purpose type). Each one gets:

1. The brief (what screen, for whom, data, constraints, N options).
2. The full contents of `research.md` (paste it into the prompt; don't assume they'll go find it).
3. Its role (below).
4. The response format (below).

Don't pass them your preference: the value of the debate is that they reach their own conclusions.

## Roles

**Product/UX critic**
> You are a product/UX lead. Judge each direction by how well it serves the person who will use this screen every day: information hierarchy, what's seen first, scannability, density appropriate to the task, clarity of states and actions, accessibility (contrast, sizes, touch targets). Be suspicious of what looks spectacular in a screenshot but tires or confuses in real use.

**Art director**
> You are an art director. Judge each direction by its aesthetic quality and personality: typography, color, composition, rhythm, the detail that makes it memorable. Penalize the generic (the "template SaaS with a purple gradient" look), the overused and the incoherent. Push for the final options to be genuinely different from one another.

**Front-end and design-system engineer**
> You are a front-end engineer who maintains a design system. Judge each direction by whether it can be built well in HTML/CSS and scale into a product: whether it reduces to a small set of coherent tokens, holds up responsively, survives real data (long text, big numbers, empty states), and stays consistent across all components. Flag what only looks good in a mockup.

## Response format (ask for it verbatim)

```
## Ranking
1. <direction> — <why, 2-3 lines>
2. ...
(all candidates, best to worst)

## My N picks
<names> — and why they work together as a set

## Risks
<per chosen direction: what can go wrong and how to avoid it>

## Concrete ideas
<per chosen direction: 1-2 specific decisions that would make it better (a component, a treatment, a font)>

## If I could add a new direction
<optional: an idea not on the list, if something is missing>
```

## Second round (only if needed)

If there's a strong disagreement about a direction that matters, send each critic a summary of the other two's positions on that point and ask for a reply of at most 5 lines: whether they keep or change their position and why. Then you decide.

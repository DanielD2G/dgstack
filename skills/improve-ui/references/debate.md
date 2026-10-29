# Subagent debate

Launch all three in a single message (Agent tool, general-purpose type) so they run in parallel. Each gets:

1. The brief: what element, what's wrong with it, constraints, N options.
2. Paths to `identity.md`, `research.md`, and the current element's source file or screenshot. Tell them to read these before answering.
3. Its role (below).
4. The response format (below).

Don't share your own preference.

## Roles

**Product/UX critic**
> You are a product/UX lead. Judge each structural direction by whether it actually fixes what's wrong with the current element for the person using it: task flow, what's seen and done first, number of steps/taps, scannability, error and empty states, touch targets and accessibility. A direction that is merely different from the current one, without being better to use, should rank low.

**Brand guardian**
> You own this product's visual identity (see identity.md). Judge each direction by whether it can be built with the existing tokens, fonts, icons and components and still feel like the same product. Flag anything that would need new colors, fonts, radii, shadows or a different illustration style, and say whether a reasonable in-brand alternative exists. Also flag directions that are on-brand but timid: the brand can stretch in structure.

**Front-end engineer**
> You maintain this codebase. Judge each direction by how it maps onto the existing components and patterns (name them), how much new component work it needs, how it behaves responsively and with real data (long names, many items, errors), and its accessibility (focus order, keyboard, ARIA). Prefer directions that compose existing pieces; flag ones that need fragile custom work.

## Response format (ask for it verbatim)

```
## Ranking
1. <direction> — <why, 2-3 lines>
...(all candidates, best to worst)

## My N picks
<names> — why they work together as a set (they should differ structurally)

## Risks
<per pick: what can go wrong and how to avoid it>

## Concrete ideas
<per pick: 1-2 specific decisions that would make it better>

## A direction that's missing (optional)
<one idea not on the list, if any>
```

## Second round (only if needed)

For a strong disagreement on a direction that matters, send each critic the other two's positions on that point and ask for at most 5 lines: keep or change, and why. Then decide.

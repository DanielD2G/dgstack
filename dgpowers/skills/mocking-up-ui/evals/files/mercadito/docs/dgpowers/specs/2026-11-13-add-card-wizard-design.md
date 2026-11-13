# Add a card from Medios de pago

Status: approved by Dani on 2026-11-13.

## Intent

Today a card can only be added in the middle of checkout, which is where
people abandon. Support gets several tickets a week from people who want
to register a card before they shop. We want an "Agregar tarjeta" entry
point on Medios de pago that walks them through it without leaving the
page.

## Goals, non-goals, anti-goals

- Goal: a customer adds a card from Medios de pago in under a minute.
- Non-goal: editing an existing card (still delete and re-add).
- Anti-goal: anything that looks like a bank form. It has to feel like
  the rest of Mercadito.

## Approaches

1. **Modal wizard on Medios de pago** (picked): three short steps in a
   modal, the page stays behind it. Keeps context, matches how the
   product already uses cards.
2. Separate page `/pagos/nueva`: simpler to build, but loses the context
   and needs its own back navigation.
3. Single long form in a modal: fewer clicks, but the address part
   overwhelms the card part, and the card check needs its own loading
   state anyway.

## Design

- "Agregar tarjeta" button on the "Tus tarjetas" card. Disabled with a
  tooltip at 5 cards ("Podés tener hasta 5 tarjetas").
- Modal wizard with three steps and a step indicator:
  1. **Tarjeta:** number, name as printed, expiry, CVV. Inline validation
     on blur. "Siguiente" verifies the card with the provider: loading
     state on the button, error inline if the provider rejects it.
  2. **Dirección de facturación:** "Usar mi dirección de entrega
     (Av. Corrientes 1847, 4° B)" checkbox, on by default, which fills and
     locks the fields. Unchecked: street, floor, zip, city.
  3. **Confirmar:** summary of the card (brand, last 4, expiry) and the
     address, "Usar como principal" switch (off by default), "Agregar
     tarjeta" button. If the final save fails: error banner, stays on the
     step.
- Back goes to the previous step keeping what was typed. Closing the
  modal asks for confirmation if anything was typed.
- On success the modal closes and the new card appears in the list with
  a short "Tarjeta agregada" toast.
- The invoices table header "Estado" is renamed to "Estado de pago".

## UI map

Flow: Medios de pago › "Agregar tarjeta" opens a modal wizard (Tarjeta →
Dirección de facturación → Confirmar), then closes back to Medios de pago
with the new card in the list and a toast.

| # | Screen / component | Source | Change | Behavior and states | Mockup |
|---|---|---|---|---|---|
| 1 | Medios de pago › Tus tarjetas card | src/pages/PaymentMethodsPage.tsx | new "Agregar tarjeta" button | opens the wizard; disabled with tooltip at 5 cards | draw |
| 2 | Add card wizard › step 1: Tarjeta | new: src/pages/AddCardWizard.tsx | new screen | inline validation errors on blur; loading on "Siguiente" while verifying; provider rejection error | draw |
| 3 | Add card wizard › step 2: Dirección de facturación | new: src/pages/AddCardWizard.tsx | new screen | checkbox on: fields filled and locked; off: editable fields | draw |
| 4 | Add card wizard › step 3: Confirmar | new: src/pages/AddCardWizard.tsx | new screen | "Usar como principal" switch; saving state; save error banner | draw |
| 5 | Medios de pago after success | src/pages/PaymentMethodsPage.tsx | new card in list + toast | toast "Tarjeta agregada", auto-dismiss | draw |
| 6 | Facturas table header | src/pages/PaymentMethodsPage.tsx | "Estado" → "Estado de pago" | none | skip: copy only |

## Left to the builder

Card number formatting and brand detection use the provider's SDK
helpers.

# Business case — margin diagnostic and decision support

## Stakeholder question

Sales growth can conceal low-margin orders. Which regions, states and product lines should a business leader investigate before changing promotion or pricing policy?

## Questions and evidence

| Question | Observed evidence | Follow-up hypothesis |
|---|---|---|
| Where is margin weaker? | Central 7.92% margin vs West 14.94% | Investigate discount exposure, segment/customer mix and loss-making categories |
| Which product groups lose money? | Tables –$17,725.48 profit on $206,965.53 sales | Examine SKU mix, freight, supplier costs and non-promotional pricing |
| Which markets deserve deep dives? | Texas –$25,729.36; Ohio –$16,971.38 | Review geography-specific pricing, fulfillment, return behavior and order mix |
| Are discounts linked to lower profit? | 30%+ discount band –$135,376.06 realized profit | Analyze profit conditional on product, geographic market and order characteristics |

## Recommended management process

1. **Diagnose:** use the SQL views and dashboards to identify marginal segments and the largest absolute loss concentrations. Confirm underlying accounting definitions before acting.
2. **Develop alternatives:** compare targeted discount ceilings, shipping-policy changes, vendor cost review and segmentation; each may have different implications for conversion.
3. **Pilot and measure:** select a suitable controlled experiment to estimate incremental net contribution, unit sales and repeat purchase behavior. Roll out only if a measured effect is favorable.

## Scenario logic

`Hypothetical recovered profit = abs(sum of negative line profits) × assumed recoverable share`

`Illustrative net profit change = hypothetical recovered profit − assumed intervention cost`

This is a **sensitivity calculation**, not an evidence-based forecast. It deliberately excludes changed order volume, product substitution, customer lifetime value and unexpected costs. At 25% recovery and $5,000 cost, the illustrative net amount is ~$34,033, not a validated opportunity.

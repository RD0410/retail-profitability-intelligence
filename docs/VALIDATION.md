# Validation and reproducibility

## Source checks

The pipeline requires 16 named columns, unique `Row ID`, nonnegative sales, discount between 0 and 1, positive quantity, parseable shipping and order dates, and ship date on or after order date. Numeric input parsing uses `Decimal` before outputs are rounded.

## Reference reconciliation

The source version used for the reference preview is expected to have:

| Metric | Expected |
|---|---:|
| Rows | 9,994 |
| Distinct orders | 5,009 |
| Distinct customers | 793 |
| Sales | $2,297,200.86 |
| Profit | $286,397.02 |

These checks are useful for catching source-version changes, corrupt files or accidental input substitutions. They are not a cryptographic provenance proof.

Each exported Tableau summary is calculated independently from cleaned rows. The SQLite mart receives the same rows and compares SQL sums/counts to the Python result.

## Tests

`python3 -m unittest discover -s tests -v`

The fixture tests cover decimal/discount bounds, weighted margins, duplicate IDs, column omission, ship-date ordering, historical reference rejection and date parsing. The complete real-data pipeline must also be run on a machine that can download the source file, or with `--source` pointing to a copy.

## Important limitations

The historical sample is fictitious, not operational data. The diagnostic tables do not control for confounding variables; discount effects, customer response and profitability improvements cannot be causally inferred from these summaries.

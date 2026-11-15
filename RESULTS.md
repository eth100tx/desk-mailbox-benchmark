# Measured results

One pass per model over both frozen tracks on November 14, 2026. A family is one delivered email and its attachments.

| Entrant | Valid /95 | Correct verdict /95 | Controlled found /42 | False alerts /46 | Unknown correct /7 | Correct marking /95 | Exact positive value /42 | Both verdicts /36 | Both verdicts + evidence /36 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| haiku | 95 | 95 | 42 | 0 | 7 | 95 | 42 | 36 | 34 |
| luna | 95 | 83 | 42 | 1 | 5 | 81 | 39 | 32 | 30 |
| bolt | 95 | 74 | 42 | 15 | 1 | 31 | 9 | 25 | 0 |
| qwen | 91 | 51 | 33 | 28 | 3 | 23 | 13 | 10 | 0 |
| ema | 95 | 53 | 27 | 24 | 4 | 39 | 5 | 6 | 0 |

## Runtime and token usage

| Entrant | Clients | Elapsed s | Families/min | Input tokens incl. cache | Output tokens | Aggregate output tok/s | API-equivalent USD |
|---|---:|---:|---:|---:|---:|---:|---:|
| haiku | 3 | 93.87 | 60.7 | 96204 | 41224 | 439.1 | 0.03763 |
| luna | 3 | 51.55 | 110.6 | 303005 | 2725 | 52.9 | 0.01186 |
| bolt | 4 | 45.64 | 124.9 | 21421 | 5613 | 123.0 | 0.00000 |
| qwen | 1 | 105.62 | 54.0 | 21147 | 3481 | 33.0 | 0.00000 |
| ema | 1 | 0.83 | 6898.4 | n/a | n/a | n/a | 0.00000 |

## Correct family verdicts by case

| Case | Families | haiku | luna | bolt | qwen | ema |
|---|---:|---:|---:|---:|---:|---:|
| binding-forward-hidden | 6 | 6 | 5 | 3 | 2 | 3 |
| binding-native-pdf | 6 | 6 | 4 | 3 | 2 | 3 |
| binding-very-hidden | 6 | 6 | 6 | 3 | 3 | 3 |
| forward-hidden | 6 | 6 | 6 | 5 | 4 | 4 |
| inline-body | 6 | 6 | 6 | 6 | 2 | 4 |
| legacy | 11 | 11 | 11 | 10 | 4 | 8 |
| missing | 6 | 6 | 4 | 0 | 2 | 3 |
| native-pdf | 6 | 6 | 6 | 6 | 3 | 4 |
| overlay-pdf | 6 | 6 | 6 | 6 | 5 | 4 |
| quoted-body | 6 | 6 | 5 | 6 | 5 | 4 |
| removed | 6 | 6 | 0 | 3 | 2 | 0 |
| scan-pdf | 6 | 6 | 6 | 6 | 3 | 3 |
| very-hidden | 6 | 6 | 6 | 5 | 4 | 4 |
| visible-sheet | 6 | 6 | 6 | 6 | 5 | 3 |
| word | 6 | 6 | 6 | 6 | 5 | 3 |

## Paired decisions with exact sources and values

The denominator includes only pairs with opposite truth. For a success both family verdicts must be correct and both positive pointers must exactly match the reference after case folding. Marking is scored separately. The six removed/missing pairs and the unpaired legacy cases contribute to family scoring.

| Case | Pairs | haiku | luna | bolt | qwen | ema |
|---|---:|---:|---:|---:|---:|---:|
| binding-forward-hidden | 3 | 3 | 2 | 0 | 0 | 0 |
| binding-native-pdf | 3 | 3 | 1 | 0 | 0 | 0 |
| binding-very-hidden | 3 | 3 | 3 | 0 | 0 | 0 |
| forward-hidden | 3 | 3 | 3 | 0 | 0 | 0 |
| inline-body | 3 | 3 | 3 | 0 | 0 | 0 |
| native-pdf | 3 | 2 | 3 | 0 | 0 | 0 |
| overlay-pdf | 3 | 3 | 3 | 0 | 0 | 0 |
| quoted-body | 3 | 3 | 2 | 0 | 0 | 0 |
| scan-pdf | 3 | 3 | 3 | 0 | 0 | 0 |
| very-hidden | 3 | 3 | 2 | 0 | 0 | 0 |
| visible-sheet | 3 | 2 | 2 | 0 | 0 | 0 |
| word | 3 | 3 | 3 | 0 | 0 | 0 |

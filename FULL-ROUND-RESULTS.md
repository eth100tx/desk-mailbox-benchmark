# Full 95-family comparison and blind forwarded-sheet test

The RTX 4090 ran Qwen3.8-27B UD-Q4_K_M with a 2,048-token reasoning allowance. Haiku used the subscription CLI. Both direct entrants received the same policy and schedule, up to four families per request, one request at a time. The first two rows exclude model initialization and read the same previously extracted packets. The historical row uses the original policy and three workers. Times include serving or CLI overhead. Output tok/s is output tokens divided by elapsed time; tokenizers and provider accounting differ. Dollar amounts are API equivalents from the CLI or zero local API charges. Power, hardware and subscription fees are excluded.

| Entrant | Verdicts /95 | Controlled found /42 | False alerts /46 ordinary | Correctly unknown /7 | Markings /95 | Positive value locations /42 | Strict pairs /36 | Seconds | Families/min | Input / output tokens | Output tok/s | USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Qwen 2,048](scores/local-qwen38-27b-2048-policy-think.json) | 94 | 41 | 0 | 7 | 94 | 41 | 36 | 1444.8 | 3.95 | 28,152 / 55,834 | 38.6 | 0.00000 |
| [Haiku, matched](scores/haiku-full95.json) | 95 | 42 | 0 | 7 | 94 | 42 | 36 | 273.3 | 20.86 | 131,537 / 49,982 | 182.9 | 0.04821 |
| [Haiku, historical](scores/haiku.json) | 95 | 42 | 0 | 7 | 95 | 42 | 34 | 93.9 | 60.72 | 96,204 / 41,224 | 439.1 | 0.03763 |

## What the direct entrants missed

Each row records a wrong verdict, marking, or required positive evidence pointer. Source and value columns show the expected and reported pointer. An asterisk means the key accepts any source. An exact pair requires both verdicts and the controlled memberâ€™s source and value.

| Entrant | Case | Family ID | Verdict (expected â†’ reported) | Marking | Source | Value |
|---|---|---|---|---|---|---|
| Qwen | legacy | df09e39ca418 | controlled â†’ ordinary | missing â†’ none | * â†’ â€” | a1/page:1 â†’ â€” |
| Haiku | legacy | a5fc04d776e9 | ordinary | none â†’ excess | * â†’ â€” | â€” |

## Blind forwarded-sheet test

We froze 24 synthetic RFC822 emails, the scoring key, and their SHA-256 commitments in commit `4dd7db8` before predictions. The model received only extracted message content and cell values. The resolver used the v1.2.0 prompt and decisions, with the original prediction loop factored into a callable function. Its rows reproduced all four archived runs exactly. Neither entrant was tuned on this holdout. The six deliberately balanced scenarios are a stress test, not a production prevalence sample. Multiple eligible private cells accept any correct witness. Correctly abstaining on a referenced missing workbook counts as correct only when no affirmative price was delivered.

A separately frozen extension adds eight forwarded sheets where two distinct vendors submitted sealed prices and the delivered rows contain both, just one, or neither. The same frozen entrants ran on all 32 messages.

| Scenario | Cases | Resolver verdict | Resolver verdict + pointers | Haiku verdict | Haiku verdict + pointers |
|---|---:|---:|---:|---:|---:|
| distinct_suppliers | 8 | 5 | 5 | 8 | 8 |
| missing_inline | 4 | 4 | 4 | 4 | 4 |
| missing_only | 4 | 4 | 4 | 4 | 4 |
| mixed_bids | 4 | 4 | 4 | 4 | 4 |
| public_bids | 4 | 4 | 4 | 4 | 4 |
| repeat_quote | 4 | 0 | 0 | 4 | 4 |
| repeat_value | 4 | 0 | 0 | 4 | 3 |
| All | 32 | 21 | 21 | 32 | 31 |

| Entrant | Parse / inference / resolver (s) | Total (s) | Input / output tokens | Output tok/s | USD | Markings /32 |
|---|---:|---:|---:|---:|---:|---:|
| Qwen resolver | 0.295 / 63.18 / 0.010 | 63.49 | 11,071 / 1,578 | 24.9 | 0.00000 | 21 |
| Haiku | 0.408 / 109.91 / 0.000 | 110.32 | 44,571 / 21,873 | 198.3 | 0.01886 | 32 |

[Resolver family outcomes](blind-sheets/outcomes.json) Â· [Haiku family outcomes](blind-sheets/haiku-outcomes.json) Â· [Native messages](blind-sheets/mail) Â· [Gold cells and markings](blind-sheets/key.json) Â· [Resolver calls](blind-sheets/predictions.json) Â· [Haiku calls](blind-sheets/haiku-predictions.json)

[Distinct-supplier source files, evidence, predictions and outcomes](blind-bids)

# Single-booking trial results

All rows use 16 extracted email families. A strict pair requires both verdicts and exact positive evidence pointers. FN includes abstentions on a controlled family. Resolved rows replay the saved labeled runs and add their measured postprocessing time. Costs and protocols are described in [the model selection report](MODEL-SELECTION.md).

### Confirmation

| Checkpoint and protocol | Verdicts | Strict pairs | FP | FN | Seconds | Input tokens | Output tokens | Output tok/s | API equivalent USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [haiku](confirmation-results/haiku.json) | 16/16 | 8/8 | 0 | 0 | 60.2 | 19227 | 6459 | 107.2 | 0.00658 |
| [local-bolt-e4b-record-labeled](confirmation-results/local-bolt-e4b-record-labeled.json) | 10/16 | 2/8 | 5 | 1 | 24.5 | 3870 | 1054 | 43.0 | 0.00000 |
| [local-bolt-e4b-record-record-match](confirmation-results/local-bolt-e4b-record-record-match.json) | 4/16 | 2/8 | 0 | 6 | 12.9 | 3088 | 946 | 73.2 | 0.00000 |
| [local-bolt-e4b-record-resolved](confirmation-results/local-bolt-e4b-record-resolved.json) | 10/16 | 2/8 | 1 | 1 | 24.5 | 3870 | 1054 | 43.0 | 0.00000 |
| [local-bolt74b-iq2-split24-policy-think](confirmation-results/local-bolt74b-iq2-split24-policy-think.json) | 10/16 | 1/8 | 5 | 1 | 344.4 | 3965 | 3722 | 10.8 | 0.00000 |
| [local-gemma4-31b-policy-think](confirmation-results/local-gemma4-31b-policy-think.json) | 16/16 | 8/8 | 0 | 0 | 476.9 | 3887 | 3834 | 8.0 | 0.00000 |
| [local-qwen38-27b-2048-policy-think](confirmation-results/local-qwen38-27b-2048-policy-think.json) | 16/16 | 8/8 | 0 | 0 | 237.7 | 4003 | 9110 | 38.3 | 0.00000 |
| [local-qwen38-27b-policy-think-single](confirmation-results/local-qwen38-27b-policy-think-single.json) | 16/16 | 8/8 | 0 | 0 | 482.5 | 10577 | 13430 | 27.8 | 0.00000 |
| [local-qwen38-27b-policy-think](confirmation-results/local-qwen38-27b-policy-think.json) | 15/16 | 5/8 | 1 | 0 | 100.5 | 4003 | 4007 | 39.9 | 0.00000 |
| [local-qwen38-27b-record-labeled](confirmation-results/local-qwen38-27b-record-labeled.json) | 1/16 | 0/8 | 0 | 7 | 22.9 | 3842 | 611 | 26.7 | 0.00000 |
| [local-qwen38-27b-record-record-match](confirmation-results/local-qwen38-27b-record-record-match.json) | 0/16 | 0/8 | 0 | 8 | 24.3 | 3092 | 780 | 32.1 | 0.00000 |
| [local-qwen38-27b-record-resolved](confirmation-results/local-qwen38-27b-record-resolved.json) | 16/16 | 8/8 | 0 | 0 | 22.9 | 3842 | 611 | 26.7 | 0.00000 |
| [local-qwen38-27b-think](confirmation-results/local-qwen38-27b-think.json) | 13/16 | 3/8 | 3 | 0 | 99.4 | 3403 | 4029 | 40.5 | 0.00000 |

### Renewal

| Checkpoint and protocol | Verdicts | Strict pairs | FP | FN | Seconds | Input tokens | Output tokens | Output tok/s | API equivalent USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [haiku](renewal-results/haiku.json) | 16/16 | 8/8 | 0 | 0 | 46.2 | 19223 | 6218 | 134.5 | 0.00646 |
| [local-bolt-e4b-record-labeled](renewal-results/local-bolt-e4b-record-labeled.json) | 14/16 | 6/8 | 2 | 0 | 17.6 | 3716 | 981 | 55.8 | 0.00000 |
| [local-bolt-e4b-record-record-match](renewal-results/local-bolt-e4b-record-record-match.json) | 0/16 | 0/8 | 0 | 8 | 12.2 | 3000 | 994 | 81.2 | 0.00000 |
| [local-bolt-e4b-record-resolved](renewal-results/local-bolt-e4b-record-resolved.json) | 14/16 | 6/8 | 0 | 0 | 17.6 | 3716 | 981 | 55.8 | 0.00000 |
| [local-gemma4-31b-policy-think](renewal-results/local-gemma4-31b-policy-think.json) | 16/16 | 4/8 | 0 | 0 | 269.5 | 3821 | 3842 | 14.3 | 0.00000 |
| [local-qwen38-27b-2048-policy-think](renewal-results/local-qwen38-27b-2048-policy-think.json) | 16/16 | 8/8 | 0 | 0 | 278.5 | 3973 | 8991 | 32.3 | 0.00000 |
| [local-qwen38-27b-policy-think-single](renewal-results/local-qwen38-27b-policy-think-single.json) | 16/16 | 5/8 | 0 | 0 | 348.9 | 10547 | 13465 | 38.6 | 0.00000 |
| [local-qwen38-27b-record-labeled](renewal-results/local-qwen38-27b-record-labeled.json) | 0/16 | 0/8 | 0 | 8 | 22.4 | 3728 | 619 | 27.7 | 0.00000 |
| [local-qwen38-27b-record-record-match](renewal-results/local-qwen38-27b-record-record-match.json) | 0/16 | 0/8 | 0 | 8 | 24.4 | 3044 | 794 | 32.6 | 0.00000 |
| [local-qwen38-27b-record-resolved](renewal-results/local-qwen38-27b-record-resolved.json) | 16/16 | 8/8 | 0 | 0 | 22.4 | 3728 | 619 | 27.7 | 0.00000 |

# Routing email families by attachment type

One decision covers the email, quoted history and all delivered attachments. Rates below count correct verdicts under the synthetic exercise policy. Each family appears once in each breakdown. The model runs used pre-extracted evidence.

| Delivered file | Families | PrismML Bonsai 2 Q2_0 | Qwen3.8-27B UD-Q4_K_M | Claude Haiku 5.5 |
|---|---:|---:|---:|---:|
| None, including referenced missing files | 23 | 20 | 23 | 23 |
| XLSX | 34 | 32 | 34 | 34 |
| PDF | 32 | 30 | 31 | 32 |
| DOCX | 6 | 6 | 6 | 6 |

| Reasoning required | Families | Bonsai | Qwen | Haiku |
|---|---:|---:|---:|---:|
| Inline or quoted body, visible sheet, Word or native PDF | 30 | 30 | 30 | 30 |
| Standard forwarded hidden or very hidden worksheet | 12 | 12 | 12 | 12 |
| Match competing lots across quoted history and delivered spreadsheet or PDF | 18 | 16 | 18 | 18 |
| Read recovered overlay or scanned PDF text | 12 | 12 | 12 | 12 |
| Decide whether a delivered PDF still contains a removed price | 6 | 5 | 6 | 6 |
| Decide from available evidence when a file is missing | 6 | 3 | 6 | 6 |
| Original mixed scenarios, including covered storage floor | 11 | 10 | 10 | 11 |

The two local models missed the same original storage-floor PDF despite having its recovered text. Bonsai also cleared three emails with missing workbooks, treated one inspected PDF with its price removed as unknown, and flagged two ordinary spreadsheets in competing-lot cases.

Run `python attachment_routing.py` to reproduce the type and scenario counts and both routing policies. The rule picks a model from delivered attachment extensions before looking up its archived prediction. The labels are used only for scoring and describing scenarios.

| Policy | Assignments | Verdicts | Markings | Controlled found | False alerts | Correct unknowns | Strict evidence pairs |
|---|---|---:|---:|---:|---:|---:|---:|
| Local | 6 Word to Bonsai, 89 others to Qwen | 94/95 | 94/95 | 41/42 | 0 | 7/7 | 36/36 |
| Hosted PDF reviewer | 6 Word to Bonsai, 32 PDF to Haiku, 57 others to Qwen | 95/95 | 95/95 | 42/42 | 0 | 7/7 | 36/36 |

These retrospective scores reuse predictions made in the original batches. The route was chosen after inspecting the public results. Grouping emails by reviewer changes batch composition. Timing, cost and end-to-end accuracy need a fresh routed run. The six Word examples provide limited evidence. A prospective test should freeze the rule, preserve the entire family as input, and include mixed attachments, mislabeled files and extraction failures. For operational use, select any hosted destination only when approved for the material.

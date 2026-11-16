# Bonsai 2 on the RTX 4090

**Bonsai scored 88/95 in 13m27s. Qwen3.8-27B scored 94/95 in 24m05s.** Both found 41 of the 42 controlled families and returned the correct value location for each detection. Bonsai made two false controlled alerts and correctly reported four of seven unknowns. Qwen made zero false alerts and got all seven unknowns right. Haiku scored 95/95 in 4m33s. [Bonsai score and every family outcome](scores/local-bonsai2-27b-q2-2048-policy-think.json) · [Qwen and Haiku comparison](FULL-ROUND-RESULTS.md)

| Full 95 families | Bonsai 2 | Qwen3.8-27B UD-Q4_K_M | Haiku 5.5 |
|---|---:|---:|---:|
| Correct markings | 87/95 | 94/95 | 94/95 |
| Both verdicts and exact evidence in matched pairs | 34/36 | 36/36 | 36/36 |
| Runtime input tokens | 28,152 | 28,152 | 131,537 |
| Output tokens | 55,884 | 55,834 | 49,982 |
| Output tokens per elapsed second | 69.2 | 38.6 | 182.9 |
| Families per minute | 7.06 | 3.95 | 20.86 |
| API-equivalent USD | 0 | 0 | 0.0482 |

Bonsai's seven verdict errors comprised the same covered reserve-floor PDF that Qwen missed, three absent workbooks treated as ordinary, one delivered PDF with its price removed treated as unknown, and two ordinary hidden-sheet families flagged as controlled in the competing-lot track. The Haiku input total includes subscription CLI context and cache accounting. Both local entrants used the same prompt and tokenizer counts. Local API cost excludes equipment and power. These are single runs on public synthetic cases. Bonsai's score on the separate 32-email blind sheet test remains unmeasured.

PrismML's Ternary-Bonsai-2-27B derives from Qwen3.8-27B. Its transformer weights use three values (-1, 0 and +1) with scaling and some higher-precision parameters. We tested the official stock llama.cpp Q2_0 text GGUF, 7,626,008,928 bytes, on the same RTX 4090 and CUDA llama.cpp b12387 as the Qwen UD-Q4_K_M reference. The GGUF SHA-256 was `4f99aed01b8a877e153f9aa6569a4440fe17c59701cc0953e36d7f460549e70e`. The most compact 5.95 GB PTQ1_0 format uses PrismML's custom kernels. [Publisher's model card and packing options](https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf/blob/839bd57023c1558945afea70a74fa83c054f35f9/README.md)

During the 16-family trials, Windows GPU Process Memory counters sampled the server at **8,732,868,608 bytes of peak observed dedicated GPU memory (8.13 GiB)**. This is process VRAM with an 8,192-token server context over two slots, running one request at a time. System RAM and a Mac's unified memory are different measurements. All trials received extracted text, including spreadsheet cells and recovered PDF text. Timings exclude download and model startup.

| Test | Bonsai verdicts | Bonsai strict pairs | Bonsai time | Qwen verdicts | Qwen strict pairs | Qwen time |
|---|---:|---:|---:|---:|---:|---:|
| [Confirmation](confirmation-results/local-bonsai2-27b-q2-2048-policy-think.json) | 16/16 | 7/8 | 129.0 s | 16/16 | 8/8 | 237.7 s |
| [Renewal](renewal-results/local-bonsai2-27b-q2-2048-policy-think.json) | 16/16 | 8/8 | 131.8 s | 16/16 | 8/8 | 278.5 s |

Both models received the clarified exercise policy, a 2,048-token reasoning allowance, temperature zero, seed 7 and four-family serial requests. In the confirmation set, Bonsai got the controlled value and the source sentence right but appended the sentence to the required literal pointer `quote`. The published strict-pair metric counts this as an error. Both 16-family sets were already public.

```text
python local_trial.py bonsai2-27b-q2-2048-policy-think <llama-server> <Ternary-Bonsai-2-27B-Q2_0.gguf> --reasoning-budget 2048 --confirmation-only
python local_trial.py bonsai2-27b-q2-2048-policy-think <llama-server> <Ternary-Bonsai-2-27B-Q2_0.gguf> --reasoning-budget 2048 --full95
```

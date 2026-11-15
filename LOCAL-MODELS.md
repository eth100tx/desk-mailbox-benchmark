# Local models on the 24 GB RTX 4090

The reference is the v1.0.0 Haiku run on the 95 frozen, extracted email families. It had 95 correct verdicts, 95 correct marking decisions, 42 exact positive value locations and 34 of 36 strict pairs. A strict pair requires both verdicts and exact pointers for the controlled value and its source. The supplemental transfer probe contains six independently worded pairs across XLSX, PDF and inline prices. The probe was written by the same team, uses synthetic packets and has six positive families. Its small size limits generalization.

[Measured comparison](LOCAL-RESULTS.md) · [Raw scores](scores) · [Transfer outputs](transfer-results)

**Use Qwen3.8-27B UD-Q4_K_M with reasoning as the first local reviewer on this workstation. Keep human review for clearance decisions.** The original prompt plus the verified scanner matched Haiku on the public verdicts, but that configuration got only 13/16 verdicts and 5/8 strict pairs on the opaque-ID confirmation set. The clarified prompt plus checks improved confirmation to 15/16 and 7/8, while giving 93/95 and 34/36 on the public round. Haiku got 16/16 and 8/8 on confirmation. No one local configuration matched Haiku on both sets. The 35B split provides no evidence for a hardware upgrade for this workflow.

The 27B Qwen reasoning run took 290.8 seconds with two local clients and zero API fees. It found all 42 controlled families and their values. The raw model got 90/95 family verdicts. Applying parser inventory and marking checks gave 94/95, leaving one false alert. A public-register consistency check corrected that alert, yielding 95/95 verdicts and 36/36 strict pairs on the public cases. Those corrections were developed on this corpus and the pre-check rows are preserved in every affected batch. The same system got 11/12 verdicts and 1/6 strict pairs on the initial paraphrase probe. Correctly finding the price did not guarantee correctly citing the provenance in quoted history.

The CPU/GPU split ran the complete corpus in 336.2 seconds, generated 16.3 aggregate output tokens/s and got 67/95 family verdicts with 19 false alerts and two missed positives. The 27B GPU-resident model with thinking disabled took 121.7 seconds and got 82/95. The split establishes feasibility on the existing hardware. Different architectures and the expert placement confound the speed difference, so this is not a same-model estimate of the offload penalty.

Gemma 4 31B IT was screened on the first two scheduled batches with reasoning enabled. It returned 11/12 correct verdicts, including a missed controlled PDF. The concurrent batches took about 138 and 167 seconds apiece, so their times must not be added as elapsed wall time. Once a miss made a perfect full-round score impossible, the screening run was stopped. Its two raw batches are retained under runs/local-gemma4-31b-think. It has no 95-case score.

| Checkpoint | Quantized file, decimal GB | SHA-256 |
|---|---:|---|
| [Qwen3.8-27B UD-Q4_K_M](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF) | 16.56 | 1bce504dfecd84153666928a41d8a66706f0158d3a317bc5196b72819d7dc529 |
| [Qwen3.6-35B-A3B UD-Q4_K_M](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF) | 22.13 | ac0e2c1189e055faa36eff361580e79c5bd6f8e76bffb4ce547f167d53e31a61 |
| [Gemma 4 31B IT Q4_K_M](https://huggingface.co/unsloth/gemma-4-31B-it-GGUF) | 18.32 | 38bd64c852c4b460434cc7162fa9bdcf242faf86502581a754cb72956bb17f84 |

A single Windows x64 llama.cpp b12387 CUDA server accepted two simultaneous requests with 4,096 tokens per slot. Approximately 18 GiB VRAM was free before loading. The 27B dense checkpoint offloaded all 66 layers. Its reported CUDA model buffer was 14,769.65 MiB and its CPU-mapped model buffer 682.03 MiB. For the 35B mixture-of-experts checkpoint the server kept the routed experts of the first 16 layers on the i9-9900K CPU. The loader reported 13,159.34 MiB of CUDA model buffers and about 7,939 MiB of CPU-mapped model buffers. These figures count weights; the server also needs context and compute buffers. Startup and download are excluded from runtime. Average wall rates include prompt processing, generation and scheduling, and are descriptive single runs on a shared workstation.

A name ending in `-think` enables the checkpoint's thinking template, with a maximum of 768 reasoning tokens per request and 2,600 total generated tokens. The policy, schema, evidence, temperature and batch schedule are otherwise the same as the standard local benchmark. The previous Haiku result used the same evidence and three concurrent subscription clients. The rule checks use the frozen parser's complete inventory. For a real scanner, a failed PDF extraction or failed OCR must remain unresolved.

```sh
python local_trial.py qwen38-27b-think /path/to/llama-server /path/to/Qwen3.8-27B-UD-Q4_K_M.gguf
python inventory_review.py local-qwen38-27b-think
python inventory_review.py local-qwen38-27b-think --check-records
python judge.py local-qwen38-27b-think-inventory local-qwen38-27b-think-verified
python local_tables.py
```

To test the model-only instruction revision, use `qwen38-27b-policy-think` as the entrant name in the first command. The runner adds the published clarification before the unchanged exercise policy. To test the split configuration, use entrant name `qwen36-35b`, its 35B GGUF, and `--cpu-experts 16`. Keep one model active at a time. For long production files, the 4,096-token per-request budget in this experiment requires additional extraction and chunking work; measured throughput here starts from pre-extracted short packets.

The inventory variant checks for an explicitly missing attachment, complete blank PDF pages, supported canonical locator spellings and the exercise marking decision. The verified variant adds one conservative grammar for a quoted list declaring each numeric lot to be a public benchmark or sealed supplier bid. It clears an otherwise flagged family only when every recognized price record matches that supported grammar and every booked identifier has an explicit, uncontested public declaration. The tool records each changed model row. These rules were developed after inspecting public-round errors. On the separate prose transfer probe, the explicit register grammar does not apply.

The join and pointer experiments use different prompts and one family per request. They were run to identify what the model and parser contribute separately. Never interpret scores from a postprocessed system as the standalone model's accuracy. The public corpus and probe are practice materials, and repeated prompt or rule development on them makes a genuinely blind test necessary before deployment.

The policy-think configuration keeps the reasoning budget, checkpoint and frozen cases and adds explicit instructions for quoted lines, missing files, empty verified pages and matching delivered records to source identifiers. It was designed after reviewing public errors and the 12-family development probe. A final 16-family confirmation set changed the wording and identifiers again, randomized opaque message IDs, and separated paired messages into different requests. The policy clarification was fixed before that set was evaluated. The confirmation results measure transfer to a related set written by the benchmark author. They do not establish equivalence across real contractor email.

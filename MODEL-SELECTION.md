# Choosing open weights for mailbox review

**Qwen3.8-27B UD-Q4_K_M with a 2,048-token reasoning allowance matched Haiku on both single-booking sets on the RTX 4090.** On each set it returned 16 correct verdicts, 16 correct marking decisions and eight strict evidence pairs in its direct output. It took 237.7 seconds on confirmation and 278.5 seconds on renewal. Haiku took 60.2 and 46.2 seconds. A single 128 GB Spark is an interesting platform for testing the 120B document model. This experiment supplies no measured Spark throughput or evidence of an accuracy advantage from purchasing one.

Model cards checked November 14, 2026. The exercise asks whether a retained price belongs to the quoted sealed bid or the public benchmark and requires the location of the retained value. Instruction following, evidence retrieval and document reasoning are relevant screening signals. Their scores use different tasks and cannot predict a mailbox score.

| Priority | Checkpoint | Reason for its place |
|---|---|---|
| Workstation reference | [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B), UD-Q4_K_M | Already measured at 15/16 on this exact test. Run one family per request as a separate protocol to test whether cross-family batching contributes to mistakes. |
| Workstation challenger | [NVIDIA Nemotron 3.5 Bolt 74B-A9B IQ2](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB-GGUF) | The October release has a 22.02 GB text weight file. NVIDIA reports AA-LCR 64.06 versus 61.06 for Qwen3.6-35B-A3B BF16 in its comparison. Actual GPU residency depends on available memory and runtime buffers. These text packets need no vision projector. |
| Independent dense control | [Google Gemma 4 31B IT](https://huggingface.co/google/gemma-4-31B-it), Q4_K_M | Different model family already available locally. Compare using the same four-family schedule as Haiku. |
| First 128 GB Spark trial | [NVIDIA Nemotron 3.5 Super VL 120B-A12B NVFP4](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-NVFP4) | NVIDIA explicitly supports a single Spark and publishes a one-sequence launch recipe. The card reports AA-LCR v1.1 of 67.69 and IFBench of 71.50, plus document and OCR evaluations. Use the same extracted families first. Measure native-page interpretation in a separate track. |
| Lower priority November fine-tune | [Smaug-Nemotron-3.5 NVFP4](https://huggingface.co/abacusai/Smaug-Nemotron-3.5-NVFP4) | Its publisher reports gains on coding and agent tasks, with long-context and instruction-following performance at parity with the Super VL parent. Start with the parent to preserve a clear comparison. |

The confirmation set has eight pairs, one underlying evidence relationship, and three representations of the retained value. Eight exact pairs means the system gets both verdicts and the required provenance and value pointers. Selecting checkpoints against this public set makes it a development set. The renewal check changes identifiers, message wording, addresses and layout and adds a DOCX paragraph representation. It still tests the same relationship and uses extracted packets. Neither track measures PST or native file extraction, legal designation, or false-positive rates in an actual contractor archive.

The production question is whether throughput and recall hold on a mailbox with low prevalence and many attachments. These 50%-positive, paired sets cannot estimate the number of alerts per thousand real messages. The earlier [95-family benchmark](RESULTS.md) exercises missing attachments, markings, revisions, images and other failure modes. The newly successful 2,048-token configuration has a measured score only on the two 16-family sets.

## What changed the result

[Complete measured results with timings, tokens, API equivalents and raw answers](SELECTION-RESULTS.md)

* Raising Qwen's reasoning allowance from 768 to 2,048 tokens kept the checkpoint, quantization, input tokens and four-family batching fixed. On confirmation the direct verdict score rose from 15 to 16, and strict pairs from five to eight. Giving the original 768-token configuration one family per call also produced 16/16 verdicts on both sets, but it located only five of the eight controlled values on renewal.
* Gemma 4 31B IT Q4_K_M got every verdict and marking right on both sets. Its raw strict-pair scores were eight on confirmation and four on renewal. All four renewal errors inserted the correct filename into an otherwise correct PDF-page or Word-paragraph pointer, such as `a1/close.pdf:page:3` for the required `a1/page:3`. This is a serialization failure and would have a different operational impact from flagging the wrong bid. The exact-match scorer was retained for every model.
* Bolt 74B IQ2's mostly GPU-resident run timed out on the second request after 300 seconds. Keeping the first 24 layers' expert weights on the CPU completed all four requests in 344 seconds. It made five false alerts, missed one controlled family, and returned one strict pair. This trial is specific to the IQ2 build and the 768-token cap. It supplies no result for the 74B BF16 model.
* Qwen without reasoning could copy both record identifiers even when its evidence-unit fields were empty or incorrect. A program that required valid model-supplied unit pointers consequently abstained on most cases. After inspecting both tracks, we added a resolver. It requires a unique unpriced passage containing the extracted private record and a unique priced passage containing the booked record. It maps the matching passage back to the attachment location. This reused the same saved predictions. Qwen plus the resolver scored 16/16 and eight strict pairs in 22.9 and 22.4 seconds. The smaller Bolt E4B plus the same resolver scored 10/16 and 14/16. Both sets had been inspected before the resolver was built; these are development scores. This method assumes one priced record and requires a supported textual price format. Repeated mentions, multiple prices and missing values can make a match ambiguous.
* The earlier JEPA-style entrant and its limitations are documented in the [original report](RESULTS.md). The newer trials did not retrain it.

## How to reproduce the protocols

Run from the repository root. Replace the two paths in angle brackets. The server binary used in these trials was CUDA llama.cpp b12387. The same packet order and exercise policy go to each grouped entrant. The local policy-think entrants also receive the published clarification about quoted history, absent identifiers and exact locators. Haiku used the original policy. Four-family calls are serial. The single-family experiment makes sixteen serial calls.

```text
python local_trial.py gemma4-31b-policy-think <llama-server> <gemma-4-31B-it-Q4_K_M.gguf> --confirmation-only
python local_trial.py bolt74b-iq2-policy-think <llama-server> <NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB.gguf> --confirmation-only
python local_trial.py bolt74b-iq2-split24-policy-think <llama-server> <NVIDIA-Nemotron-3.5-Bolt-74B-A9B-24GB.gguf> --confirmation-only --cpu-experts 24
python local_trial.py qwen38-27b-2048-policy-think <llama-server> <Qwen3.8-27B-UD-Q4_K_M.gguf> --confirmation-only --reasoning-budget 2048
python local_trial.py qwen38-27b-policy-think <llama-server> <Qwen3.8-27B-UD-Q4_K_M.gguf> --confirmation-only --single
python local_trial.py qwen38-27b-record <llama-server> <Qwen3.8-27B-UD-Q4_K_M.gguf> --record-match
python local_trial.py bolt-e4b-record <llama-server> <Nemotron-3.5-Bolt-E4B-Q4_K_M.gguf> --record-match
python local_trial.py qwen38-27b-record <llama-server> <Qwen3.8-27B-UD-Q4_K_M.gguf> --record-match --labeled
python local_trial.py bolt-e4b-record <llama-server> <Nemotron-3.5-Bolt-E4B-Q4_K_M.gguf> --record-match --labeled
python resolve_records.py local-qwen38-27b-record
python resolve_records.py local-bolt-e4b-record
python confirmation.py haiku --track renewal
python selection_tables.py
python verify_selection.py
```

The direct reasoning entrants use temperature zero, seed 7, an 8,192-token server context divided over two slots, a 768-token reasoning cap unless labeled 2048, and a schema-constrained response. They return verdicts, markings and locators directly. The record-match entrant is specialized for a single booking and a quoted private supplier record. The model extracts both identifiers and their evidence units, then Python checks that the strings occur in the chosen units, compares the identifiers, maps units to native locators, and applies the banner rule. The entrant has no access to labels during inference. It requires separate evaluation before use on multiple bookings, rankings or absent files.

Bolt 74B text GGUF SHA-256: `91d63363e782c8a3d5f4be42816eba8e0d42dd2530bd07a7d0d2dc440599af75`. Other local weight digests are in [local model notes](LOCAL-MODELS.md). Timings exclude download and model initialization, include prompt processing and response generation, and were taken on a shared desktop. A weight download overlapped part of the first Gemma run. Output tokens per second use total generated tokens divided by elapsed trial time. Haiku amounts are the subscription CLI's reported API-equivalent usage. Local trials used zero paid API calls. Equipment, power and subscription fees are excluded.

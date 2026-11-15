# Can the winning local configuration handle the rest of the mailbox?

On the full 95 families, Qwen correctly classified 94, flagged 41 of the 42 controlled cases and issued zero false alerts. Its one miss was a PDF whose recovered text still disclosed a private reserve floor of USD 2.18 per unit. Haiku found that disclosure and got 95/95 verdicts. Its only marking error treated “CUI training is at 11” as a banner on a public agenda. Both systems got all 36 strict evidence pairs. Qwen took 24m05s against Haiku’s 4m33s on the matched schedule. A model download overlapped part of the local run.

[Measured results and missed cases](FULL-ROUND-RESULTS.md) · [Sealed holdout manifest](blind-sheets/commitment.json) · [Earlier model comparison](MODEL-SELECTION.md)

The original 95 families were already public when we selected Qwen3.8-27B. This run measures transfer across media and failure modes under the challenge’s fictional policy. Its 95 cases are the original 77 plus 18 record-binding cases. Qwen used the same UD-Q4_K_M weights, clarified policy, temperature zero, seed 7, 2,048-token reasoning cap, 2,600-token output limit and serial batches of up to four as its two successful 16-family runs. Haiku was rerun with the same input text, family order and batch boundaries through the subscription CLI. Haiku and Qwen have different tokenizers, decoding controls and output handling.

The new stress test contains 24 native RFC822 messages written for this round. Sixteen carry actual XLSX attachments with hidden or very hidden registers. The other eight reference an absent workbook. Four of the latter disclose a private amount inline. Multiple priced rows can include both public and private offers. Repeated identifiers appear either in forwarded source text or in distinct priced rows. Every message has an opaque identifier. Predictors receive the extractor’s body, sheet names, visibility, coordinates and values. No answer key or case category goes into a model request. The released key makes the round reproducible and turns it into a public practice set for future entrants.

The fast pipeline uses Qwen without thinking to copy one private and one booked record ID and uses ordinary code to resolve unique passages. A claimed controlled result must have an exact source and an eligible cell or body pointer. An ordinary or unknown result must carry empty pointers. Where two sealed prices are present, either correct cell qualifies. That metric measures the ability to identify a controlled family and support it with one witness. Exhaustive reporting of every sensitive cell is a different task.

## Reproduce

The frozen resolver classified 21/32 correctly, with eight unnecessary abstentions (four controlled, four ordinary) when source IDs or priced IDs were repeated. In three distinct-supplier cases it called a controlled sheet ordinary. For example, it extracted TX-42291 as private and TX-99889 as booked. Both were sealed supplier records. TX-99889 was delivered at Register!B4, but the single-record comparison only tested whether the two extracted IDs were equal. The resolver correctly distinguished all four missing-workbook cases requiring an unknown verdict from all four cases with a retained private amount in the body. Haiku got 32/32 verdicts and 31/32 exact witnesses. In its one formatting miss it returned both eligible repeated-value cells separated by a semicolon where the contract expects one. Resolver and Haiku took 63.49 and 110.32 seconds respectively for the 32 families, including native email and workbook extraction. Use the fast system as an evidence aid. Its ordinary output does not establish that all private bids were checked.

The additional eight native emails in [the distinct-supplier cohort](blind-bids) were committed in `d380ac3` before either entrant processed them. They contain two distinct sealed suppliers and identical prices. The workbook retains both private IDs, just one, or neither. The blind commands below process both cohorts.

Use the checked-in messages and run from the repository root. Install the dependencies in `requirements.txt`. Replace the server and weights paths with local paths. The release uses llama.cpp CUDA b12387. Each local command acquires the same loopback server port, runs its track, and unloads the model. Reproduction writes new timestamps and timings into the run directories.

```text
python local_trial.py qwen38-27b-2048-policy-think <llama-server> <Qwen3.8-27B-UD-Q4_K_M.gguf> --reasoning-budget 2048 --full95
python evaluate.py haiku-full95 --workers 1 --batch-size 4
python evaluate.py haiku-full95 --workers 1 --batch-size 4 --binding
python judge.py haiku-full95
python local_trial.py qwen38-27b-record <llama-server> <Qwen3.8-27B-UD-Q4_K_M.gguf> --blind
python blind_sheet.py score
python blind_sheet.py predict --model haiku
python blind_sheet.py score --model haiku
python full_round_report.py
```

For offline verification, run the two blind scoring commands and the report command against the saved predictions. The blind scorer validates all original message hashes and the key before scoring. The full-round report recomputes both 95-case scores from the raw batches and checks them against their published score files. Regenerating native emails can change MIME boundaries and workbook timestamps; use the frozen bytes for the published comparison.

## The 120B NVFP4 checkpoint on this workstation

NVIDIA’s exact Nemotron 3.5 Super VL 120B-A12B NVFP4 checkpoint had 88 safetensors weight shards totaling **75,010,188,240 bytes (69.86 GiB)** at inspection. The GGML organization’s NVFP4 GGUF text file alone was 76.92 GB. The workstation reported 47.92 GiB of visible host RAM, 23.99 GiB total GPU memory, and about **11.44 GiB host RAM plus 18.33 GiB VRAM free** immediately before the local trial. Even treating those free pools as perfectly additive leaves a roughly 40 GiB shortfall for the official shards before inference buffers. The loaded expert subset per token does not shrink the complete checkpoint. The disk-backed trial uses a memory-mapped GGUF, CPU-resident expert operations and GPU offload of the other layers. Its conditions differ from Spark’s native NVFP4 runtime. GPU-resident deployment of the complete checkpoint is infeasible here. NVIDIA lists a single DGX Spark as a supported deployment. [Official weights](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-NVFP4/tree/main) · [GGUF files](https://huggingface.co/ggml-org/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-GGUF/tree/main) · [NVIDIA’s Spark recipe](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-NVFP4)

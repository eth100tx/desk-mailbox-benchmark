# Reproduce or enter

Download the frozen repository or the tagged release. For a new entrant, use only the release's **entrant.zip**. It includes policy.txt, native EML files, extracted packets and batch schedules, with no answer keys, generator or model outputs. Work offline or use an independently authorized model service. The public repository includes the answers for reproduction. It is a practice event.

## Verify and rescore

Python 3.10.6 was used on Windows. From the repository root run the following commands. Recomputing scores uses only Python's standard library.

```sh
python judge.py
python tables.py
python -m pip install -r requirements.txt
python verify.py
```

The verifier checks frozen file hashes, schedule separation, identical data bytes per attachment pair, actual worksheet visibility, exact prices at labeled positive locations, white PDF renders and retained versus removed text. For independent OCR readback, set TESSDATA_PREFIX to a folder containing eng.traineddata from tessdata_fast with SHA-256 7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2 and run `python verify.py --ocr`. The basic verifier uses the frozen OCR packets for scan-only pages. [English OCR weights](https://github.com/tesseract-ocr/tessdata_fast/blob/main/eng.traineddata)

Native files are frozen for byte-level replication. In a separate disposable copy of the repository, run `python dataset.py` and `python binding.py` to regenerate synthetic cases. The 11 legacy native fixtures are inputs to regeneration. The committed schedules are part of the experimental design. Office ZIP timestamps, PDF document IDs and MIME boundaries can change on regeneration, so verify the original manifest against the original files. The extraction path uses openpyxl, python-docx and PyMuPDF, with Tesseract English OCR for image-only pages.

## Run the entrants

The shared policy is in policy.txt. Inputs are ordered using the provided schedules. The 77-family main track uses 14 requests of five or six families each. The 18-family binding track uses four requests of four or five families. The two sides of each pair always appear in different requests. All models see the same extracted evidence and policy. Hosted models used their subscription clients, which add their own system prompts and output handling. The CLI removes direct API-key environment overrides. Confirm subscription login before running a hosted entrant.

```sh
python evaluate.py ema
python evaluate.py ema --binding
python evaluate.py qwen
python evaluate.py qwen --binding
python evaluate.py haiku --workers 3
python evaluate.py haiku --binding --workers 3
python evaluate.py luna --workers 3
python evaluate.py luna --binding --workers 3
python serve_bolt.py /path/to/llama-server /path/to/Nemotron-3.5-Bolt-E4B-Q4_K_M.gguf
python judge.py
python tables.py
```

Run in a fresh copy to preserve the published outputs. Qwen uses Ollama 0.6.8 at localhost:11434, qwen2.5:14b, Q4_K_M, model ID 7cdf5a0187d5, one client, 8,192 context tokens and a 1,600-output-token cap. Bolt uses llama.cpp b12387 CUDA, driver 621.14, temperature zero, four slots of 4,096, a 1,600-output-token cap, disabled prompt caching and zero reasoning budget. NVIDIA's Bolt GGUF SHA-256 is c8af2b8aea10a690a1d9491db744a9446660173cb38fc489612b556615a69612. [Bolt weights](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Bolt-E4B-4GB) · [llama.cpp build](https://github.com/ggml-org/llama.cpp/releases/tag/b12387)

Haiku used Claude Code 2.1.318 and the Max subscription. The observed resolved model name was claude-haiku-5-5. Luna used codex-cli 0.166.0, the ChatGPT login and exact requested model gpt-6-luna. On Windows, set CODEX_EXE to the native codex.exe. The Luna adapter rejects evidence of shell, file-change, web or MCP tool calls in returned events. Each hosted request uses an ephemeral or nonpersistent session in a fresh temporary directory. Provider updates can change outputs and timing. The release keeps original answers and usage to support deterministic rescoring.

Timing is the sum of the two evaluation windows per entrant. It includes request dispatch, response parsing and saving the outputs. It excludes extraction, artifact generation, judging and Bolt server startup. Qwen's first request can include model load. EMA fitting took another 2.36 seconds across its two process launches. The models ran on a shared desktop, one GPU model at a time. Cloud tests could overlap. These are single-pass, workload-level rates, not isolated hardware decode speeds or confidence intervals.

API equivalents are USD estimates, not subscription charges. Haiku uses the CLI's per-request list-cost telemetry including cached tokens. Luna uses standard input at $0.10/million, cached input at $0.01/million and output at $0.50/million, with cached input subtracted from full-rate input. Input totals include client overhead and caches. Output tokens include any reasoning counted by the provider. Tokenizers, parallelism and reasoning differ. EMA generates no tokens. Local runs have zero API fees; hardware, electricity and subscription allocations are excluded. [OpenAI standard pricing](https://developers.openai.com/api/docs/pricing) · [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)

## Score another system

Return one JSON object per line, with id, verdict, source, value and issue. The required vocabulary is in policy.txt. Send the JSONL to the organizer or use the public scorer yourself.

```sh
python score_entry.py my-entry.jsonl
```

This round scores three-way family verdicts, marking and exact evidence pointers. It does not measure probability calibration. The judge reports false controlled alerts separately from ordinary families sent to unknown. A blank or invalid row does not receive credit. For the published runs, an invented or duplicated ID cannot fill a missing row. The standalone scorer rejects malformed submissions so entrants can repair their transport before submitting. Legacy source pointers were never adjudicated, so exact value location is the applicable localization metric there. Across 36 opposite-verdict pairs, full credit requires both verdicts and both pointers on the positive side. The headline binding result uses nine of those pairs with balanced word counts.

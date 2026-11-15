# Local challengers to Haiku

Scores are from the same frozen 95 email families. The last column is a separate 12-family paraphrase probe with six opposite-verdict pairs. Each pair requires both correct verdicts and the correct source and value pointers. A dash means no recorded probe.

| Entrant | Correct /95 | False alerts /46 | Missed controlled /42 | Marking /95 | Exact value /42 | Strict pairs /36 | Hard pairs /9 | Time, s | Output tok/s | Fresh strict pairs /6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| haiku | 95 | 0 | 0 | 95 | 42 | 34 | 9 | 93.9 | 439.1 | 6 |
| local-bolt-join | 68 | 27 | 0 | 68 | 42 | 9 | 9 | 91.6 | 22.6 | — |
| local-qwen36-35b | 67 | 19 | 2 | 39 | 16 | 0 | 0 | 336.2 | 16.3 | 0 |
| local-qwen38-27b-join | 74 | 21 | 0 | 74 | 42 | 15 | 9 | 89.3 | 11.5 | 0 |
| local-qwen38-27b-pointers | 53 | 0 | 42 | 53 | 0 | 0 | 0 | 110.2 | 17.2 | 0 |
| local-qwen38-27b-policy-think-verified | 93 | 0 | 1 | 93 | 41 | 34 | 9 | 408.2 | 47.7 | 3 |
| local-qwen38-27b-policy-think | 90 | 3 | 1 | 89 | 40 | 31 | 6 | 407.8 | 47.8 | 3 |
| local-qwen38-27b-think-inventory | 94 | 1 | 0 | 94 | 42 | 35 | 8 | 290.9 | 63.5 | 1 |
| local-qwen38-27b-think-verified | 95 | 0 | 0 | 95 | 42 | 36 | 9 | 290.8 | 63.6 | 1 |
| local-qwen38-27b-think | 90 | 1 | 0 | 89 | 42 | 35 | 8 | 290.8 | 63.6 | 1 |
| local-qwen38-27b | 82 | 5 | 1 | 81 | 19 | 5 | 0 | 121.7 | 46.9 | 3 |

## Opaque-ID confirmation check

Sixteen further email packets use eight matched pairs, randomized opaque IDs, new booking labels, and different source wording. Both decisions and both pointers must match. These samples were authored on this project and are small. The separate 12-family probe above used patterned IDs and should be treated as exploratory.

| Entrant | Raw verdict /16 | Raw strict /8 | Verified verdict /16 | Verified strict /8 |
|---|---:|---:|---:|---:|
| haiku | 16 | 8 | 16 | 8 |
| local-qwen38-27b-policy-think | 15 | 5 | 15 | 7 |
| local-qwen38-27b-think | 13 | 3 | 13 | 5 |

Elapsed time excludes model download and startup. Output tok/s is the sum of generated tokens divided by batch wall time. Different output lengths, provider accounting and concurrency make families per elapsed second more relevant to archive processing. Each local entrant used zero paid API calls.

Plain local entrants use the frozen policy, grouped prompts and temperature zero. Names ending in -think enable a 768-token reasoning budget. The policy-think revision adds explicit evidence conventions. Suffixes -inventory and -verified denote postprocessing of the same saved model calls. The join entrant asks the model to identify private numeric lot references and uses code to match referenced lots to delivered prices. Its fallback selects a single evidence item. The pointers entrant gives the model a numbered inventory of body lines and attachment units for one family per call. The model chooses source and value IDs. Code resolves their file locations, checks for a missing attachment and evaluates the marking. The two adapters were developed with knowledge of the public practice round. Their scores measure the complete system and should not be attributed to the checkpoint alone.

The fresh probe uses renamed references, changed worksheet addresses and phrasing that places the public and private identifiers in running prose. It tests one provenance relationship across six pairs and is too small to establish production equivalence. The probe uses extracted packets directly.

To reproduce the larger-model trials run local_trial.py with a name, a CUDA llama-server executable and a GGUF filename. Add --guided to run the structured adapters and --cpu-experts 16 to keep the first 16 layers' routed expert weights on the CPU for the MoE trial. Each entrant has a full raw run and score file under runs and scores. Execute python local_tables.py to regenerate this table.

"""Render the new entrants alongside the fixed reference without changing the original leaderboard."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
def main():
    names=["haiku",*[f.stem for f in sorted((ROOT/"scores").glob("local-*.json"))]]
    lines=["# Local challengers to Haiku","",
        "Scores are from the same frozen 95 email families. The last column is a separate 12-family paraphrase probe with six opposite-verdict pairs. Each pair requires both correct verdicts and the correct source and value pointers. A dash means no recorded probe.","",
        "| Entrant | Correct /95 | False alerts /46 | Missed controlled /42 | Marking /95 | Exact value /42 | Strict pairs /36 | Hard pairs /9 | Time, s | Output tok/s | Fresh strict pairs /6 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name in names:
        r=json.loads((ROOT/"scores"/(name+".json")).read_text());s=r["summary"];t=r["timing"]
        path=ROOT/"transfer-results"/(name+".json")
        fresh=json.loads(path.read_text())["summary"]["pair_linked"] if path.exists() else "—"
        hard=sum(v["pair_linked"] for k,v in r["case"].items() if k.startswith("binding-"))
        row=[name,s["verdict"],s["fp"],s["pos"]-s["tp"],s["mark"],s["locations"],s["pair_linked"],hard,round(t["seconds"],1),round(t["output_tokens_s"],1),fresh]
        lines.append("| "+" | ".join(map(str,row))+" |")
    lines+=["","## Opaque-ID confirmation check","","Sixteen further email packets use eight matched pairs, randomized opaque IDs, new booking labels, and different source wording. Both decisions and both pointers must match. These samples were authored on this project and are small. The separate 12-family probe above used patterned IDs and should be treated as exploratory.","","| Entrant | Raw verdict /16 | Raw strict /8 | Verified verdict /16 | Verified strict /8 |","|---|---:|---:|---:|---:|"]
    for f in sorted((ROOT/"confirmation-results").glob("*.json")):
        report=json.loads(f.read_text());raw=report["raw"];verified=report["verified"]
        lines.append(f'| {f.stem} | {raw["verdict"]} | {raw["pair_linked"]} | {verified["verdict"]} | {verified["pair_linked"]} |')
    lines+=["","Elapsed time excludes model download and startup. Output tok/s is the sum of generated tokens divided by batch wall time. Different output lengths, provider accounting and concurrency make families per elapsed second more relevant to archive processing. Each local entrant used zero paid API calls.","",
        "Plain local entrants use the frozen policy, grouped prompts and temperature zero. Names ending in -think enable a 768-token reasoning budget. The policy-think revision adds explicit evidence conventions. Suffixes -inventory and -verified denote postprocessing of the same saved model calls. The join entrant asks the model to identify private numeric lot references and uses code to match referenced lots to delivered prices. Its fallback selects a single evidence item. The pointers entrant gives the model a numbered inventory of body lines and attachment units for one family per call. The model chooses source and value IDs. Code resolves their file locations, checks for a missing attachment and evaluates the marking. The two adapters were developed with knowledge of the public practice round. Their scores measure the complete system and should not be attributed to the checkpoint alone.","",
        "The fresh probe uses renamed references, changed worksheet addresses and phrasing that places the public and private identifiers in running prose. It tests one provenance relationship across six pairs and is too small to establish production equivalence. The probe uses extracted packets directly.","",
        "To reproduce the larger-model trials run local_trial.py with a name, a CUDA llama-server executable and a GGUF filename. Add --guided to run the structured adapters and --cpu-experts 16 to keep the first 16 layers' routed expert weights on the CPU for the MoE trial. Each entrant has a full raw run and score file under runs and scores. Execute python local_tables.py to regenerate this table."]
    (ROOT/"LOCAL-RESULTS.md").write_text("\n".join(lines)+"\n",encoding="utf8")
if __name__=="__main__":main()

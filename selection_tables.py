"""Print the 16-family trial tables from saved model responses."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for track in ("confirmation", "renewal"):
    print(f"\n### {track.title()}\n")
    print("| Checkpoint and protocol | Verdicts | Strict pairs | FP | FN | Seconds | Input tokens | Output tokens | Output tok/s | API equivalent USD |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for path in sorted((ROOT / (track + "-results")).glob("*.json")):
        result = json.loads(path.read_text())
        summary = result["raw"]
        usage = [r["usage"] for r in result["runs"]]
        inp = sum(u.get("input", u.get("prompt_tokens", 0)) for u in usage)
        out = sum(u.get("output", u.get("completion_tokens", 0)) for u in usage)
        dollars = sum(u.get("usd", 0) for u in usage)
        sec = result["seconds"]
        print(f"| [{path.stem}]({path.relative_to(ROOT).as_posix()}) | {summary['verdict']}/16 | "
              f"{summary['pair_linked']}/8 | {summary['fp']} | {summary['pos']-summary['tp']} | {sec:.1f} | "
              f"{inp} | {out} | {out/sec:.1f} | {dollars:.5f} |")

"""Score a new competitor's JSONL submission on the frozen 95 families."""
import argparse,json
from collections import Counter
from pathlib import Path
from judge import ROOT,read,counts,score_rows
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("submission",type=Path);a=p.parse_args()
    key={**read(ROOT/"data/key.json"),**read(ROOT/"data/binding/key.json")}
    rows={}
    for line in a.submission.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():continue
        r=json.loads(line)
        if not all(isinstance(r.get(k),str) for k in ["id","verdict","source","value","issue"]):raise ValueError("Missing string field")
        if r["id"] not in key or r["id"] in rows:raise ValueError("Unknown or duplicate id")
        if r["verdict"] not in {"unknown","controlled","ordinary"} or r["issue"] not in {"correct","wrong-category","missing","none","excess","unknown"}:raise ValueError("Invalid decision")
        rows[r["id"]]=r
    print(json.dumps(counts(key,score_rows(key,rows)),indent=2))

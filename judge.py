"""Score the two frozen input tracks, per-case outcomes and reproducible run accounting."""
import json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MODELS=["ema","qwen","bolt","haiku","luna"]
def read(p): return json.loads(p.read_text(encoding="utf8"))
def write(p,x):p.write_text(json.dumps(x,indent=2)+"\n",encoding="utf8")
def score_rows(key,rows):
    outcomes={}
    for ident,k in key.items():
        r=rows.get(ident,{})
        label=r.get("verdict")
        correct=label==k["verdict"]
        loc=correct and r.get("value","").casefold()==k["value"].casefold()
        linked=loc and (k["source"] is None or r.get("source","").casefold()==k["source"].casefold())
        outcomes[ident]=dict(kind=k["kind"],truth=k["verdict"],reported=label,correct=correct,mark=r.get("issue")==k["issue"],
            value=loc,linked=linked,expected_value=k["value"],reported_value=r.get("value"),reported_source=r.get("source"))
    return outcomes
def counts(key,outcomes):
    known=[k for k in outcomes if key[k]["verdict"]=="controlled"]
    ordinary=[k for k in outcomes if key[k]["verdict"]=="ordinary"]
    unknown=[k for k in outcomes if key[k]["verdict"]=="unknown"]
    pairs=defaultdict(list)
    for i in outcomes:
        if key[i]["pair"]:pairs[key[i]["pair"]].append(i)
    eligible=[v for v in pairs.values() if {key[i]["verdict"] for i in v}=={"controlled","ordinary"} and len(v)==2]
    def success(pair):
        return all(outcomes[i]["correct"] and (key[i]["verdict"]!="controlled" or outcomes[i]["linked"]) for i in pair)
    return dict(n=len(outcomes),valid=sum(x["reported"] is not None for x in outcomes.values()),
        pos=len(known),tp=sum(outcomes[i]["correct"] for i in known),neg=len(ordinary),fp=sum(outcomes[i]["reported"]=="controlled" for i in ordinary),
        unknown=len(unknown),unknown_ok=sum(outcomes[i]["correct"] for i in unknown),verdict=sum(x["correct"] for x in outcomes.values()),
        locations=sum(outcomes[i]["value"] for i in known),mark=sum(x["mark"] for x in outcomes.values()),pairs=len(eligible),
        pair_verdicts=sum(all(outcomes[i]["correct"] for i in v) for v in eligible),pair_linked=sum(success(v) for v in eligible))
def collect(model):
    keys={};reports={};runmetrics=[];seconds=0;fit=0;invalid=[];workers=[]
    for binding in [False,True]:
        folder=ROOT/"data"/("binding" if binding else "")
        key=read(folder/"key.json");keys.update(key);schedule=read(folder/"schedule.json")
        dest=ROOT/"runs"/(model+("-binding" if binding else ""))
        timing=read(dest/"timing.json");seconds+=timing["seconds"];workers.append(timing["workers"])
        for n,ids in enumerate(schedule):
            result=read(dest/f"{n:02}.json");assert ids==result["ids"]
            if n==0:fit+=result["usage"].get("fit_s",0)
            runmetrics.append(result["usage"])
            rows=result["rows"]
            ids_returned=Counter(r.get("id") for r in rows if isinstance(r,dict))
            for r in rows:
                if not isinstance(r,dict) or not all(isinstance(r.get(f),str) for f in ["id","verdict","value","source","issue"]):continue
                if r["id"] not in ids or ids_returned[r["id"]]!=1 or r["verdict"] not in {"ordinary","controlled","unknown"} or r["issue"] not in {"missing","correct","none","wrong-category","unknown","excess"}:continue
                reports[r["id"]]=r
            if set(ids_returned)!=set(ids) or any(v!=1 for v in ids_returned.values()):invalid.append([binding,n,dict(ids_returned)])
    outcomes=score_rows(keys,reports)
    case={name:counts(keys,{i:v for i,v in outcomes.items() if v["kind"]==name}) for name in sorted({v["kind"] for v in outcomes.values()})}
    nout=sum(u["output"] or 0 for u in runmetrics)
    return dict(summary=counts(keys,outcomes),case=case,outcomes=outcomes,invalid_batches=invalid,
                timing=dict(seconds=seconds,fit_seconds=fit,workers=workers,input_tokens=sum(u["input"] or 0 for u in runmetrics) if model!="ema" else None,
                output_tokens=nout if model!="ema" else None,output_tokens_s=nout/seconds if model!="ema" else None,
                usd=sum(u["usd"] for u in runmetrics),families_min=len(keys)*60/seconds))
if __name__=="__main__":
    out=ROOT/"scores";out.mkdir(exist_ok=True)
    for m in sys.argv[1:] or MODELS:
        result=collect(m);write(out/(m+".json"),result);print(m,result["summary"],result["timing"])

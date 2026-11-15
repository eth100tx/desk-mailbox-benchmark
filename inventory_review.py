"""Apply inventory and locator checks to saved model output, with a full edit trail."""
import argparse,json,re,time
from copy import deepcopy
from collections import defaultdict
from pathlib import Path
from judge import ROOT,read,write,counts,score_rows
from local_join import units
from transfer_probe import fixtures
PRICE=re.compile(r"(?:\b\d+\.\d+\b|(?:[$€£]|\b(?:USD|EUR|GBP)\s*)\d+|\b\d+\s*(?:USD|EUR|GBP|per MWh)|\b(?:rank(?:s|ed)?|plac(?:es|ed))\s+(?:first|second|third|\d+))",re.I)
def canonical(pointer,legal):
    if not pointer:return pointer
    exact=[p for p in legal if p.casefold()==pointer.casefold()]
    if len(exact)==1:return exact[0]
    if pointer.lower().startswith("quote:paragraph:") and "quote" in legal:return "quote"
    match=re.match(r"^(a\d+)/(.+)$",pointer,re.I)
    if not match:return pointer
    part,tail=match[1].casefold(),match[2].casefold()
    hits=[p for p in legal if p.lower().startswith(part+"/") and any(tail.endswith(sep+p.split("/",1)[1].lower()) for sep in ("!","/"," ",", "))]
    return hits[0] if len(hits)==1 else pointer
def explicitly_public_records(packet):
    """Establish complete public coverage only for the supported register grammar."""
    declarations=defaultdict(set)
    for line in packet["body"].splitlines():
        match=re.fullmatch(r"\s*>?\s*Lot\s+(\d+)\s*:\s*source is (the public benchmark|a sealed supplier bid)\.\s*",line,re.I)
        if match:declarations[match[1]].add(match[2].lower())
        elif line.lstrip().startswith(">") and line.lstrip("> ").strip():return False
    if not declarations:return False
    booked=[]
    for loc,text in units(packet):
        if not PRICE.search(text):continue
        # A partial match could hide a second value or an unrelated private fact.
        record=re.fullmatch(r"\s*Lot\s+(\d+)[\s|=]+(\d+\.\d+)(?:\s+USD(?:/MWh)?)?\s*",text,re.I)
        if not record:return False
        booked.append(record[1])
    return bool(booked) and all(declarations[id]=={"the public benchmark"} for id in booked)
def review(packet,row,check_records=False):
    result=dict(row);body=packet["body"];a=packet["attachments"]
    paths={"body","quote"}|{loc for loc,_ in units(packet)}
    for field in ["source","value"]:result[field]=canonical(result[field],paths)
    body_disclosure=bool(PRICE.search(body))
    missing=not a and bool(re.search(r"\battached\b",body,re.I))
    # Only valid on a track with independently verified complete extraction.
    empty_pdf=bool(a) and all(x["filename"].lower().endswith(".pdf") and x["entries"] and
                   all(not entry[-1].strip() for entry in x["entries"]) for x in a)
    if not body_disclosure and (missing or empty_pdf):
        result.update(verdict="unknown" if missing else "ordinary",value="",source="")
    if check_records and result["verdict"]=="controlled" and explicitly_public_records(packet):
        result.update(verdict="ordinary",value="",source="")
    banner=re.search(r"^\s*CUI\s*(?://\s*([A-Z]+))?\s*$",body,re.M|re.I)
    v=result["verdict"]
    result["issue"]=("unknown" if v=="unknown" else ("excess" if banner else "none") if v=="ordinary"
                    else "missing" if not banner else "wrong-category" if banner.group(1) else "correct")
    return result
def main():
    parser=argparse.ArgumentParser();parser.add_argument("model");parser.add_argument("--check-records",action="store_true");args=parser.parse_args()
    extension="-verified" if args.check_records else "-inventory"
    for suffix,track in [("",""),("-binding","binding")]:
        data=ROOT/"data"/track;packets={p["id"]:p for p in read(data/"packets.json")}
        source=ROOT/"runs"/(args.model+suffix);dest=ROOT/"runs"/(args.model+extension+suffix);dest.mkdir(exist_ok=True)
        start=time.perf_counter()
        for f in sorted(source.glob("[0-9]*.json")):
            record=read(f);edits={}
            for i,row in enumerate(record["rows"]):
                if row["id"] not in packets:continue
                updated=review(packets[row["id"]],row,args.check_records)
                if updated!=row:edits[row["id"]]=row
                record["rows"][i]=updated
            record["before_inventory_checks"]=edits;write(dest/f.name,record)
        timing=read(source/"timing.json");timing["postprocess_seconds"]=time.perf_counter()-start
        timing["seconds"]+=timing["postprocess_seconds"];write(dest/"timing.json",timing)
    src=ROOT/"transfer-results"/(args.model+".json")
    if src.exists():
        original=read(src);packets,key,_=fixtures();out={}
        for id,r in original["outcomes"].items():
            if r["reported"] is not None:
                out[id]=review(packets[id],dict(id=id,verdict=r["reported"],value=r["reported_value"],source=r["reported_source"],issue="unknown"),args.check_records)
        outcomes=score_rows(key,out)
        write(src.with_name(args.model+extension+".json"),dict(summary=counts(key,outcomes),outcomes=outcomes,derived_from=src.name))
if __name__=="__main__":main()

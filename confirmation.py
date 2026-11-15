"""A second small transfer check. Entrant IDs are opaque and pair members run in separate prompts."""
import hashlib,json,random,time
from evaluate import ROOT,generate,clean_json
from judge import score_rows,counts
from inventory_review import review
def cases():
    packets={};key={};groups=[[],[]];rng=random.Random(93317)
    for i in range(8):
        a,b=rng.sample(range(100,999),2)
        prefix=["Order","Hub","Entry","Account"][i%4]
        booked,absent=f"{prefix} {a}",f"{prefix} {b}"
        price=round(23+rng.random()*60,2)
        for row in range(2):
            ident=f"{rng.getrandbits(64):016x}"
            restricted,market=(booked,absent) if row==0 else (absent,booked)
            src=[f"> The exchange circular is the source for {market}.",f"> The sealed supplier envelope is the source for {restricted}."]
            if i%2:src.reverse()
            body="Please reconcile the single booking against yesterday's source notes.\n"+"\n".join(src)
            if i%3==0:
                cell=f"Detail!F{i+6}"
                entries=[[cell.replace("F","C"),"hidden",booked],[cell,"hidden",str(price)]]
                att=[dict(filename="ledger.xlsx",entries=entries)];loc="a1/"+cell
            elif i%3==1:
                att=[dict(filename="ledger.pdf",entries=[["page:1","Desk register"],["page:2",f"USD {price} was booked against {booked}."]])]
                loc="a1/page:2"
            else:
                body+=f"\nBooked USD {price} for {booked}.";att=[];loc="body"
            packets[ident]=dict(id=ident,subject="Desk close",body=body,attachments=att)
            key[ident]=dict(kind="confirmation",pair=str(i),verdict=["controlled","ordinary"][row],
                            issue=["missing","none"][row],source=["quote",""][row],value=[loc,""][row])
            groups[(i+row)%2].append(ident)
    for g in groups:rng.shuffle(g)
    return packets,key,[block[j:j+4] for block in groups for j in range(0,len(block),4)]
def main(model):
    packets,key,groups=cases();rows={};runs=[];start=time.perf_counter()
    for ids in groups:
        ans,u=generate(model,(ROOT/"policy.txt").read_text()+"\nEvidence:\n"+json.dumps([packets[i] for i in ids],ensure_ascii=False))
        runs.append(dict(ids=ids,answer=ans,usage=u))
        try:
            for r in clean_json(ans):
                if r["id"] in ids:rows[r["id"]]=r
        except (KeyError,TypeError,ValueError):pass
    checks={k:review(packets[k],r,True) for k,r in rows.items()}
    out=ROOT/"confirmation-results";out.mkdir(exist_ok=True)
    result=dict(seconds=time.perf_counter()-start,raw=counts(key,score_rows(key,rows)),verified=counts(key,score_rows(key,checks)),runs=runs)
    (out/(model+".json")).write_text(json.dumps(result,indent=2))
    print(model,result["raw"],flush=True)
if __name__=="__main__":
    import sys
    main(sys.argv[1])

"""Small fresh extracted-packet probe, authored after model adapters were frozen."""
import argparse,json,time
from pathlib import Path
from evaluate import ROOT,clean_json,generate
from local_join import emit
from judge import counts,score_rows
def fixtures():
    cases=[];key={};groups=[[],[]]
    for i,(handle,other,kind) in enumerate([
        ("Lot 822","Lot 129","sheet"),("Ticket GA-18","Ticket RN-77","sheet"),
        ("Lot 278","Lot 640","pdf"),("Delivery Red","Delivery Blue","pdf"),
        ("Lot 107","Lot 853","inline"),("Quote PX-9","Quote JH-4","inline")]):
        for side in range(2):
            ident=f"probe-{i}-{side}";price="17.83"
            private,public=(handle,other) if side==0 else (other,handle)
            note=f"> We can circulate {public} now that it appears in the exchange bulletin.\n> Please keep {private} within the tender team until the submissions are opened."
            body="For reconciliation. Only the booked record is enclosed.\n"+note
            if kind=="sheet":
                att=[dict(filename="settlements.xlsx",entries=[["Rates!A5","hidden","Record"],["Rates!B5","hidden","USD"],["Rates!A8","hidden",handle],["Rates!B8","hidden",price]])]
                val="a1/Rates!B8"
            elif kind=="pdf":
                att=[dict(filename="settlements.pdf",entries=[["page:1","Settlement register"],["page:2",f"{handle}   {price} USD"]])]
                val="a1/page:2"
            else:
                att=[];body+=f"\nThe booked line is {handle} at USD {price}."
                val="body"
            cases.append(dict(id=ident,subject="Settlement check",body=body,attachments=att))
            groups[(side+i)%2].append(ident)
            key[ident]=dict(kind=kind,pair=f"probe-{i}",verdict="controlled" if side==0 else "ordinary",
                issue="missing" if side==0 else "none",source="quote" if side==0 else "",value=val if side==0 else "")
    return {p["id"]:p for p in cases},key,groups
def main():
    a=argparse.ArgumentParser();a.add_argument("model");args=a.parse_args()
    packets,key,groups=fixtures();rows={};usage=[];answers=[]
    start=time.perf_counter()
    if args.model.endswith(("-join","-pointers")):
        decide=emit
        if args.model.endswith("-pointers"):
            from local_pointers import emit as decide
        for ids in groups:
            for id in ids:
                r,u,answer=decide(packets[id]);rows[id]=r;usage.append(u);answers.append(answer)
    else:
        for ids in groups:
            answer,u=generate(args.model,(ROOT/"policy.txt").read_text()+"\nEvidence:\n"+json.dumps([packets[i] for i in ids],ensure_ascii=False))
            answers.append(answer);usage.append(u)
            try:
                for row in clean_json(answer):
                    if row["id"] in ids:rows[row["id"]]=row
            except (TypeError,ValueError,KeyError):pass
    elapsed=time.perf_counter()-start
    o=score_rows(key,rows);s=counts(key,o)
    target=ROOT/"transfer-results";target.mkdir(exist_ok=True)
    (target/(args.model+".json")).write_text(json.dumps(dict(seconds=elapsed,summary=s,outcomes=o,answers=answers,usage=usage),indent=2))
    print(args.model,s)
if __name__=="__main__":main()

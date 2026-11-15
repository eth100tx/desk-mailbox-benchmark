"""Generate the forwarded-sheet holdout, run predictions without the key, then score."""
import argparse
import hashlib
import json
import random
import time
from email import policy
from email.message import EmailMessage
from pathlib import Path

from dataset import attachment, extract
from record_match import extract as model_extract
from evaluate import clean_json, generate as classify
from resolve_records import resolve_rows

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "blind-sheets"
MAIL = DATA / "mail"


def save(name, obj):
    (DATA / name).write_bytes((json.dumps(obj, indent=2) + "\n").encode())


def read(name):
    return json.loads((DATA / name).read_bytes())


def generate():
    rng = random.Random(771398)
    MAIL.mkdir(parents=True, exist_ok=True)
    key = {}
    for scenario in ("mixed_bids", "public_bids", "repeat_quote", "repeat_value", "missing_only", "missing_inline"):
        for j in range(4):
            ident = f"{rng.getrandbits(96):024x}"
            sealed, public, other = (f"R-{n}" for n in rng.sample(range(17000, 99800), 3))
            price = round(rng.uniform(20, 87), 2)
            picks = [f"> Vendor envelope {sealed} remains sealed until award.",
                     f"> {public} and {other} are published exchange benchmarks."]
            rows = [(public, price)]
            truth = "controlled"
            if scenario == "mixed_bids":
                rows += [(sealed, price), (other, price + 1)]
            elif scenario == "public_bids":
                rows += [(other, price)]
                truth = "ordinary"
            elif scenario == "repeat_quote":
                picks.append(f"> For the log: the confidential supplier return was {sealed}.")
                rows = [(sealed if j < 2 else public, price)]
                truth = "controlled" if j < 2 else "ordinary"
            elif scenario == "repeat_value":
                ref = sealed if j < 2 else public
                rows = [(ref, price), (ref, round(price + 2.17, 2))]
                truth = "controlled" if j < 2 else "ordinary"
            elif scenario == "missing_only":
                truth = "unknown"
            rng.shuffle(picks)
            rng.shuffle(rows)
            banner = "CUI\n" if j % 2 else ""
            body = banner + "Carrying the desk's close forward.\n" + "\n".join(picks)
            msg = EmailMessage(policy=policy.SMTP)
            msg["Message-ID"] = f"<{ident}@desk.example>"
            msg["From"], msg["To"] = "ledger@desk.example", "review@desk.example"
            msg["Subject"] = "FW: desk close"
            absent = scenario.startswith("missing")
            if absent:
                body += "\nPlease reconcile the attached closing workbook."
            if scenario == "missing_inline":
                body += f"\nAmount already booked for {sealed}: USD {price:.2f}."
            msg.set_content(body)
            cells = []
            if not absent:
                name, raw, _ = attachment("very-hidden" if j % 2 else "forward-hidden", rows, 0)
                msg.add_attachment(raw, maintype="application", subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",filename=name)
                cells = [f"a1/Register!B{k}" for k,(ref,_) in enumerate(rows,2) if ref == sealed]
            elif scenario == "missing_inline":
                cells = ["body"]
            (MAIL / (ident+".eml")).write_bytes(msg.as_bytes())
            issue = ("unknown" if truth=="unknown" else ("correct" if banner else "missing") if truth=="controlled"
                     else ("excess" if banner else "none"))
            key[ident] = dict(scenario=scenario,verdict=truth,issue=issue,source="quote" if cells else "",values=cells)
    save("key.json",key)
    save("commitment.json",dict(key_sha256=hashlib.sha256((DATA/"key.json").read_bytes()).hexdigest(),
        messages={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(MAIL.glob("*.eml"))}))


def generate_distinct():
    rng=random.Random(489513)
    MAIL.mkdir(parents=True,exist_ok=True)
    key={}
    for j in range(8):
        ident=f"{rng.getrandbits(96):024x}"
        a,b,c,d=[f"TX-{v}" for v in rng.sample(range(10000,99999),4)]
        notes=[f"> Larch returned {a} in its sealed proposal.",f"> Elm submitted {b} under sealed cover.",
               f"> Exchange closing benchmarks are {c} and {d}."]
        rng.shuffle(notes)
        refs=[[a,b,c],[b,c,d],[c,d],[a,c,d]][j%4]
        rng.shuffle(refs)
        rows=[(ref,49.37) for ref in refs]
        msg=EmailMessage(policy=policy.SMTP)
        msg["Message-ID"]=f"<{ident}@desk.example>"
        msg["From"],msg["To"]="ledger@desk.example","review@desk.example"
        msg["Subject"]="FW: close schedule"
        banner="CUI\n" if j>=4 else ""
        msg.set_content(banner+"Here are the rows carried into this close.\n"+"\n".join(notes))
        name,raw,_=attachment("very-hidden" if j>=4 else "forward-hidden",rows,0)
        msg.add_attachment(raw,maintype="application",subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",filename=name)
        (MAIL/(ident+".eml")).write_bytes(msg.as_bytes())
        vals=[f"a1/Register!B{k}" for k,ref in enumerate(refs,2) if ref in (a,b)]
        key[ident]=dict(scenario="distinct_suppliers",verdict="controlled" if vals else "ordinary",
                        issue=("correct" if banner else "missing") if vals else ("excess" if banner else "none"),
                        source="quote" if vals else "",values=vals)
    save("key.json",key)
    save("commitment.json",dict(key_sha256=hashlib.sha256((DATA/"key.json").read_bytes()).hexdigest(),
        messages={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(MAIL.glob("*.eml"))}))


def predict(model="resolver"):
    start = time.perf_counter()
    packets = {p.stem:extract(p) for p in sorted(MAIL.glob("*.eml"))}
    parsed = time.perf_counter()
    calls = []
    rows = {}
    if model == "resolver":
        calls = [model_extract(p,labeled=True)[1] for p in packets.values()]
    else:
        items = list(packets.values())
        for i in range(0,len(items),4):
            batch = items[i:i+4]
            answer,usage = classify("haiku-full95",(ROOT/"policy.txt").read_text()+"\nEvidence:\n"+json.dumps(batch,ensure_ascii=False))
            calls.append(dict(ids=[p["id"] for p in batch],answer=answer,usage=usage))
            entries=clean_json(answer)
            assert sorted(r["id"] for r in entries)==sorted(p["id"] for p in batch)
            rows.update({r["id"]:r for r in entries})
    inferred = time.perf_counter()
    if model == "resolver":
        rows = resolve_rows(packets,calls)
    end = time.perf_counter()
    prefix = "" if model=="resolver" else "haiku-"
    save(prefix+"predictions.json",dict(rows=rows,runs=calls,seconds=end-start,parse_seconds=parsed-start,
                                 inference_seconds=inferred-parsed,resolve_seconds=end-inferred))


def score(model="resolver"):
    commitment = read("commitment.json")
    assert hashlib.sha256((DATA/"key.json").read_bytes()).hexdigest() == commitment["key_sha256"]
    assert {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in MAIL.glob("*.eml")} == commitment["messages"]
    prefix = "" if model=="resolver" else "haiku-"
    predictions,key = read(prefix+"predictions.json"),read("key.json")
    assert set(key)==set(predictions["rows"])
    results = {}
    for ident,k in key.items():
        r = predictions["rows"][ident]
        ok = r["verdict"]==k["verdict"]
        evidence = r["value"] in k["values"] and r["source"]==k["source"] if k["values"] else not r["value"] and not r["source"]
        results[ident]=dict(scenario=k["scenario"],expected=k["verdict"],reported=r["verdict"],correct=ok,
                            mark=r["issue"]==k["issue"],exact=ok and evidence)
    save(prefix+"outcomes.json",results)


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=["generate","predict","score"])
    parser.add_argument("--model",choices=["haiku","resolver"],default="resolver")
    parser.add_argument("--track",choices=["original","distinct","all"],default="all")
    args=parser.parse_args()
    for track in (["original","distinct"] if args.track=="all" else [args.track]):
        DATA=ROOT/("blind-sheets" if track=="original" else "blind-bids")
        MAIL=DATA/"mail"
        if args.action=="generate":
            (generate if track=="original" else generate_distinct)()
        else:{"predict":predict,"score":score}[args.action](args.model)

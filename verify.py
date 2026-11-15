"""Verify native MIME, public packet readback, paired attachment hashes and judge inventory."""
import argparse,hashlib,json,re
from email import policy
from email.parser import BytesParser
from pathlib import Path
from collections import defaultdict
import fitz
from dataset import ROOT,extract
def digest(raw):return hashlib.sha256(raw).hexdigest()
def verify(folder,ocr):
    key=json.loads((folder/"key.json").read_text())
    packets={p["id"]:p for p in json.loads((folder/"packets.json").read_text())}
    schedule=json.loads((folder/"schedule.json").read_text())
    ids=[i for batch in schedule for i in batch]
    assert len(ids)==len(set(ids)) and set(ids)==set(key)==set(packets)=={f.stem for f in (folder/"mail").glob("*.eml")}
    batches={i:n for n,batch in enumerate(schedule) for i in batch}
    groups=defaultdict(list)
    for i,k in key.items():
        p=packets[i];f=folder/"mail"/(i+".eml");msg=BytesParser(policy=policy.default).parsebytes(f.read_bytes())
        assert str(msg["Message-ID"])==f"<{i}@desk.example>"
        if ocr or k["kind"]!="scan-pdf":assert p==extract(f)
        if not k["pair"]:continue
        groups[k["pair"]].append(i)
        a=list(msg.iter_attachments())
        if a:assert digest(a[0].get_payload(decode=True))==k["attachment_sha256"]
        if k["kind"]=="scan-pdf":
            with fitz.open(stream=a[0].get_payload(decode=True),filetype="pdf") as doc:assert all(not p.get_text().strip() and p.get_images() for p in doc)
        if k["kind"] in {"removed","overlay-pdf"}:
            with fitz.open(stream=a[0].get_payload(decode=True),filetype="pdf") as doc:
                for page in doc:
                    pix=page.get_pixmap()
                    assert min(pix.samples)==255
                    assert bool(page.get_text().strip())==(k["kind"]=="overlay-pdf")
                if k["kind"]=="overlay-pdf":assert doc.version_count>1
        if k["kind"] in {"forward-hidden","very-hidden","binding-forward-hidden","binding-very-hidden"}:
            states=[v[1] for v in p["attachments"][0]["entries"] if v[0].startswith("Register!")]
            assert states and set(states)=={"veryHidden" if "very-hidden" in k["kind"] else "hidden"}
        if k["verdict"]=="controlled" and k["value"].startswith("a1/"):
            loc=k["value"].split("/",1)[1];entry=next(e for e in p["attachments"][0]["entries"] if e[0]==loc)
            assert float(k["price"]) in [float(t) for t in re.findall(r"\d+(?:\.\d+)?",entry[-1])]
    for pair,(a,b) in groups.items():
        assert batches[a]!=batches[b]
        assert key[a]["price"]==key[b]["price"] and key[a]["attachment_sha256"]==key[b]["attachment_sha256"]
        if pair.startswith("binding"):
            words=lambda i:sorted(re.findall(r"[\w.]+",packets[i]["body"].lower()))
            assert words(a)==words(b)
    return len(key),len(groups)
if __name__=="__main__":
    cli=argparse.ArgumentParser();cli.add_argument("--ocr",action="store_true");a=cli.parse_args()
    print([verify(ROOT/"data"/folder,a.ocr) for folder in ["","binding"]])
    for manifest in [ROOT/"SHA256SUMS",ROOT/"LOCAL-SHA256SUMS"]:
        if not manifest.exists():continue
        for line in manifest.read_text().splitlines():
            h,name=line.split("  ",1);assert digest((ROOT/name).read_bytes())==h,name
        print(manifest.name,"verified")

"""Lexically balanced holdout: private and public source descriptions appear on both sides."""
import json,random,hashlib
from email import policy
from email.message import EmailMessage
from dataset import DATA,attachment,extract
def main():
    folder=DATA/"binding"
    (folder/"mail").mkdir(parents=True,exist_ok=True)
    rng=random.Random(78442); packets=[]; key={}; sides=[[],[]]
    for i in range(9):
        kind=["forward-hidden","very-hidden","native-pdf"][i%3]
        tags=[f"Lot {n}" for n in rng.sample(range(100,999),3)]
        slot=(i//3+i)%2
        rows=[(tags[2],51.16)]*2
        rows[slot]=(tags[0],42.61)
        name,raw,loc=attachment(kind,rows,slot)
        for side in range(2):
            ident=f"{rng.getrandbits(48):012x}";sides[(i+side)%2].append(ident)
            sealed,public=tags[side],tags[1-side]
            lines=[f"> {sealed}: source is a sealed supplier bid.",f"> {public}: source is the public benchmark."]
            if i%2: lines.reverse()
            body="Forwarding the two entries actually booked.\n\n"+"\n".join(lines+[f"> {tags[2]}: source is the public benchmark."])
            m=EmailMessage(policy=policy.SMTP);m["Message-ID"]=f"<{ident}@desk.example>";m["From"]="ledger@desk.example";m["To"]="review@desk.example";m["Subject"]="FW: booked lots";m.set_content(body)
            subtype="pdf" if name.endswith("pdf") else "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            m.add_attachment(raw,maintype="application",subtype=subtype,filename=name)
            path=folder/"mail"/(ident+".eml");path.write_bytes(m.as_bytes());packets.append(extract(path))
            key[ident]=dict(kind="binding-"+kind,pair=f"binding-{i}",side=["sealed","public"][side],verdict=["controlled","ordinary"][side],
                issue=["missing","none"][side],source=["quote",""][side],value=["a1/"+loc,""][side],reference=tags[0],price=42.61,attachment_sha256=hashlib.sha256(raw).hexdigest())
    schedule=[]
    for half in sides:
        rng.shuffle(half)
        schedule.extend([half[:5],half[5:]])
    for name,obj in [("key",key),("packets",sorted(packets,key=lambda p:p["id"])),("schedule",schedule)]:
        (folder/(name+".json")).write_text(json.dumps(obj,indent=2)+"\n")
if __name__=="__main__":main()

"""Generate matched fictional RFC822 messages and extract the public evidence track."""
import hashlib, io, json, os, random, tempfile
from pathlib import Path
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from docx import Document
import fitz
import openpyxl

ROOT=Path(__file__).resolve().parent
DATA=ROOT/"data"
KINDS=["forward-hidden","very-hidden","visible-sheet","quoted-body","inline-body","word","native-pdf","overlay-pdf","scan-pdf","removed","missing"]
def save(name,obj):
    (DATA/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf8")

def attachment(kind,rows,slot):
    buf=io.BytesIO()
    if kind in KINDS[:3]:
        book=openpyxl.Workbook()
        main=book.active
        main.title="Summary"
        main.append(["Morning reconciliation","See source register"])
        tab=book.create_sheet("Register")
        tab.sheet_state={"very-hidden":"veryHidden","forward-hidden":"hidden","visible-sheet":"visible"}[kind]
        tab.append(["Reference","USD per MWh"])
        for item in rows: tab.append(item)
        book.save(buf)
        return "desk.xlsx",buf.getvalue(),f"Register!B{slot+2}"
    if kind=="word":
        doc=Document()
        doc.core_properties.author="Fictional Desk"
        for a,b in rows: doc.add_paragraph(f"{a}    {b:.2f} USD/MWh")
        doc.save(buf)
        return "desk.docx",buf.getvalue(),f"paragraph:{slot+1}"
    if kind in ["quoted-body","inline-body","missing"]: return None,None,"quote" if kind=="quoted-body" else "body"
    with fitz.open() as doc:
        for a,b in rows:
            page=doc.new_page(width=480,height=160)
            page.insert_text((25,70),f"{a}    {b:.2f} USD/MWh",fontsize=22)
        if kind=="scan-pdf":
            with fitz.open() as raster:
                for page in doc:
                    p=raster.new_page(width=480,height=160)
                    p.insert_image(p.rect,stream=page.get_pixmap(matrix=fitz.Matrix(2,2)).tobytes("png"))
                data=raster.tobytes()
        elif kind=="overlay-pdf":
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/"page.pdf"
                doc.save(path)
                with fitz.open(path) as edit:
                    for page in edit: page.draw_rect(page.rect,color=None,fill=(1,1,1),overlay=True)
                    edit.saveIncr()
                data=path.read_bytes()
        elif kind=="removed":
            for page in doc:
                page.add_redact_annot(page.rect)
                page.apply_redactions()
            data=doc.tobytes(garbage=4,deflate=True)
        else: data=doc.tobytes()
    return "desk.pdf",data,f"page:{slot+1}"

def extract(path):
    msg=BytesParser(policy=policy.default).parsebytes(path.read_bytes())
    packet=dict(id=str(msg["Message-ID"]).strip("<>").split("@")[0],subject=str(msg["Subject"]),body=msg.get_body().get_content().strip(),attachments=[])
    for part in msg.iter_attachments():
        name=part.get_filename()
        raw=part.get_payload(decode=True)
        entries=[]
        if name.endswith("xlsx"):
            for tab in openpyxl.load_workbook(io.BytesIO(raw),read_only=True):
                for row in tab.iter_rows():
                    entries.extend([[f"{tab.title}!{c.coordinate}",tab.sheet_state,str(c.value)] for c in row if c.value is not None])
        elif name.endswith("docx"):
            entries=[[f"paragraph:{i}",p.text] for i,p in enumerate(Document(io.BytesIO(raw)).paragraphs,1)]
        else:
            with fitz.open(stream=raw,filetype="pdf") as doc:
                for i,p in enumerate(doc,1):
                    txt=p.get_text().strip()
                    if not txt and p.get_images():
                        txt=p.get_text(textpage=p.get_textpage_ocr(language="eng",dpi=220,full=True,tessdata=os.environ["TESSDATA_PREFIX"])).strip()
                    entries.append([f"page:{i}",txt])
        packet["attachments"].append(dict(filename=name,entries=entries))
    return packet

def main():
    mail=DATA/"mail"
    mail.mkdir(parents=True,exist_ok=True)
    rng=random.Random(481153)
    key={}
    packets=[]
    for k,kind in enumerate(KINDS):
        for v in range(3):
            slot=(k+v)%2
            ref=rng.sample(range(200,900),2)
            rows=[(f"Lot {a}",round(rng.uniform(32,88),2)) for a in ref]
            if k==v==0: rows[slot]=(rows[slot][0],42.61)
            name,raw,loc=attachment(kind,rows,slot)
            for sealed in [True,False]:
                ident=f"{rng.getrandbits(48):012x}"
                tag=rows[slot][0]
                statement=(["The supplier lodged this under seal.","This came from the unopened tender file.","The vendor restricted circulation to the bid desk."] if sealed else
                           ["The exchange has published this benchmark.","This came from yesterday's open tariff bulletin.","The market desk released this index to everyone."])[v]
                provenance=f"{tag}: {statement} The other lot is a public index."
                banner=["","CUI\n","CUI//PRIVACY\n"][(v+k)%3]
                body=banner+"Please reconcile the referenced line for the morning desk.\n\n> Forwarded source note\n> "+provenance
                if kind=="inline-body": body+="\n\n"+" / ".join(f"{a} = {b:.2f}" for a,b in rows)
                if kind=="quoted-body": body+="\n> "+" / ".join(f"{a} = {b:.2f}" for a,b in rows)
                if kind=="missing": body+="\nThe register is attached."
                mid=f"<{ident}@desk.example>"
                m=EmailMessage(policy=policy.SMTP)
                m["From"]="settlements@desk.example";m["To"]="review@desk.example"
                m["Subject"]="FW: morning reconciliation";m["Message-ID"]=mid
                m.set_content(body)
                if name:
                    m.add_attachment(raw,maintype="application",subtype={"pdf":"pdf","xlsx":"vnd.openxmlformats-officedocument.spreadsheetml.sheet","docx":"vnd.openxmlformats-officedocument.wordprocessingml.document"}[name.split(".")[-1]],filename=name)
                path=mail/(ident+".eml")
                path.write_bytes(m.as_bytes())
                target="unknown" if kind=="missing" else "controlled" if sealed and kind!="removed" else "ordinary"
                issue="unknown" if target=="unknown" else ("missing" if not banner else "wrong-category" if "PRIVACY" in banner else "correct") if target=="controlled" else ("excess" if banner else "none")
                key[ident]=dict(kind=kind,pair=f"{kind}-{v}",side="sealed" if sealed else "public",verdict=target,issue=issue,
                    source="quote" if target=="controlled" else "",value=(("a1/" if name else "")+loc) if target=="controlled" else "",
                    reference=tag,price=rows[slot][1],attachment_sha256=hashlib.sha256(raw).hexdigest() if raw else None)
                packets.append(extract(path))
    legacy=json.loads((DATA/"legacy-key.json").read_text())
    for ident in legacy: packets.append(extract(mail/(ident+".eml")))
    key.update(legacy)
    packets.sort(key=lambda p:p["id"])
    save("packets.json",packets)
    save("key.json",key)
if __name__=="__main__": main()

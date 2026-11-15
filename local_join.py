"""Development entrant: local semantic decisions with deterministic lot joins and native locators."""
import argparse,concurrent.futures,json,re,time
from collections import defaultdict
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parent
LOT=re.compile(r"\blot\s+(\d+)\b",re.I)
AMOUNT=re.compile(r"\b(\d+\.\d+)\b")
def units(p):
    for line in p["body"].splitlines():
        if line.strip():yield ("quote" if line.lstrip().startswith(">") else "body"),line
    for i,a in enumerate(p["attachments"],1):
        prefix=f"a{i}/"
        if a["filename"].lower().endswith(".xlsx"):
            groups=defaultdict(list)
            for addr,_,value in a["entries"]:
                sheet,cell=addr.rsplit("!",1)
                groups[sheet,re.search(r"\d+$",cell).group()].append((addr,value))
            for row in groups.values():
                numeric=[addr for addr,v in row if AMOUNT.fullmatch(v)]
                yield prefix+(numeric or [row[0][0]])[0]," | ".join(v for _,v in row)
        else:
            for loc,value in a["entries"]:yield prefix+loc,value
def emit(p):
    content=list(units(p))
    sources={}
    values=defaultdict(list)
    for loc,text in content:
        for match in LOT.finditer(text):
            tail=text[match.end():]
            if loc in {"body","quote"} and re.match(r"\s*:",tail):
                sources[match[1]]=(loc,tail.split(":",1)[1].strip())
            elif re.match(r"[\s|=$]*\d+\.\d+\b",tail):
                values[match[1]].append(loc)
    choices=["none"]
    if sources:
        choices += list(sources)
        prompt=("Which listed lot, if any, has a source that is a private supplier tender under the exercise policy? "
                "An unpublished offer or a vendor's circulation restriction qualifies. A public index does not. "
                "Choose the private lot even when its amount was not supplied; the caller separately inspects the delivered values. "
                +json.dumps({k:v[1] for k,v in sources.items()}))
    else:
        choices += [str(i) for i in range(len(content))]
        prompt=("Select the SINGLE evidence item that actually discloses a sealed vendor bid amount, internal storage reserve floor, or private bidder ranking or margin. "
                "Select none for public data, cover notes, banners, or a reference without the actual value. "
                +json.dumps([dict(index=i,text=text) for i,(_,text) in enumerate(content)]))
    schema={"type":"object","properties":{"selection":{"type":"string","enum":choices}},"required":["selection"],"additionalProperties":False}
    reply=requests.post("http://127.0.0.1:18172/v1/chat/completions",json=dict(messages=[dict(role="user",content=prompt)],temperature=0,seed=7,max_tokens=64,cache_prompt=False,chat_template_kwargs={"enable_thinking":False},response_format={"type":"json_schema","json_schema":{"name":"choice","schema":schema}}),timeout=180)
    reply.raise_for_status();raw=reply.json(); ans=raw["choices"][0]["message"]["content"]
    value=src=""
    try: choice=json.loads(ans)["selection"]
    except (ValueError,KeyError,TypeError):choice=None
    if sources and choice in values and choice in sources:
        src=sources[choice][0];value=values[choice][0]
    elif not sources and choice in choices[1:]:
        value=src=content[int(choice)][0]
    absent=not p["attachments"] and re.search(r"\battached\b",p["body"],re.I)
    verdict="controlled" if value else "unknown" if absent or choice not in choices else "ordinary"
    banner=re.search(r"^\s*CUI\s*(?://\s*([A-Z]+))?\s*$",p["body"],re.M|re.I)
    issue=("unknown" if verdict=="unknown" else ("excess" if banner else "none") if verdict=="ordinary"
           else "missing" if not banner else "wrong-category" if banner.group(1) else "correct")
    return dict(id=p["id"],verdict=verdict,source=src,value=value,issue=issue),raw["usage"],dict(prompt=prompt,answer=ans)
def main():
    a=argparse.ArgumentParser();a.add_argument("name");a.add_argument("--workers",type=int,default=2);a.add_argument("--binding",action="store_true");args=a.parse_args()
    folder=ROOT/"data"/("binding" if args.binding else "")
    dest=ROOT/"runs"/(args.name+("-binding" if args.binding else ""));dest.mkdir(exist_ok=True)
    packets={p["id"]:p for p in json.loads((folder/"packets.json").read_text())}
    start=time.perf_counter()
    decide=emit
    if args.name.endswith("-pointers"):
        from local_pointers import emit as decide
    with concurrent.futures.ThreadPoolExecutor(args.workers) as pool:
        for i,ids in enumerate(json.loads((folder/"schedule.json").read_text())):
            t=time.perf_counter();results=list(pool.map(decide,[packets[k] for k in ids]))
            rows,usages,answers=zip(*results)
            usage=dict(input=sum(u["prompt_tokens"] for u in usages),output=sum(u["completion_tokens"] for u in usages),usd=0,model=args.name)
            (dest/f"{i:02}.json").write_text(json.dumps(dict(ids=ids,rows=rows,usage=usage,answers=answers,seconds=time.perf_counter()-t),indent=2))
    (dest/"timing.json").write_text(json.dumps(dict(seconds=time.perf_counter()-start,workers=args.workers)))
if __name__=="__main__":main()

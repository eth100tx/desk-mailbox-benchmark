"""One family per call. Models select supplied evidence IDs; a deterministic adapter emits rows."""
import json,re
import requests
from local_join import units
def emit(p):
    passages=list(units(p))
    inventory={f"E{i}":loc for i,(loc,_) in enumerate(passages,1)}
    rendered=[f"E{i} [{loc}] {text}" for i,(loc,text) in enumerate(passages,1)]
    prompt=("Review the WHOLE delivered family under this fictional desk policy. Find a disclosed private sealed supplier amount, "
            "unreleased storage reserve price, or internal bidder ranking/margin. An ordinary price, public benchmark, "
            "banner or statement that a private bid exists is insufficient. Match the identity in the source statement to the "
            "actual priced row. If only public rows were delivered, choose none. An absent or blank price is no disclosure. "
            "For a disclosure select the evidence ID containing the actual value, and the ID establishing its private source. "
            "They can be different, or identical for a self-contained statement. Use none for both when no controlled "
            "value is disclosed. The caller handles missing files and marking. Inspect all of the following evidence.\n"
            +"\n".join(rendered))
    choices=list(inventory)+["none"]
    option={"type":"string","enum":choices}
    schema={"type":"object","properties":{"value":option,"source":option},"required":["value","source"],"additionalProperties":False}
    r=requests.post("http://127.0.0.1:18172/v1/chat/completions",json=dict(messages=[dict(role="user",content=prompt)],temperature=0,
        seed=7,max_tokens=160,cache_prompt=False,chat_template_kwargs={"enable_thinking":False},
        response_format={"type":"json_schema","json_schema":{"name":"evidence","schema":schema}}),timeout=180)
    r.raise_for_status();raw=r.json();ans=raw["choices"][0]["message"]["content"]
    try:
        choice=json.loads(ans);value=inventory.get(choice["value"],"");source=inventory.get(choice["source"],"")
        valid=choice["value"] in choices and choice["source"] in choices
    except (ValueError,TypeError,KeyError):value=source="";valid=False
    absent=not p["attachments"] and re.search(r"\battached\b",p["body"],re.I)
    verdict="controlled" if value else "unknown" if absent or not valid else "ordinary"
    b=re.search(r"^\s*CUI\s*(?://\s*([A-Z]+))?\s*$",p["body"],re.M|re.I)
    issue=("unknown" if verdict=="unknown" else ("excess" if b else "none") if verdict=="ordinary" else
           "missing" if not b else "wrong-category" if b.group(1) else "correct")
    return dict(id=p["id"],verdict=verdict,source=source if value else "",value=value,issue=issue),raw["usage"],dict(prompt=prompt,answer=ans)

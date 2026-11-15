"""Entrant for the single-booking track. Extract two record keys and compare them."""
import argparse
import json
import re
import time

import requests

import confirmation
import renewal
from judge import ROOT, counts, score_rows
from local_join import units


def extract(packet, labeled=False):
    inventory = {str(i): unit for i, unit in enumerate(units(packet), 1)}
    fields = ("private_record", "source_unit", "booked_record", "amount_unit")
    prompt = (
        "Extract facts from this one delivered email. Copy the full record identifier "
        "named by the nonpublic supplier offer into private_record, and its unit number "
        "into source_unit. Independently copy the full record identifier accompanying "
        "the retained numeric price into booked_record, and its unit number into amount_unit. "
        "Preserve all letters, punctuation and digits of each identifier. The two records "
        "may differ. Use an empty string for missing facts. Use only the supplied evidence.\n"
        + json.dumps(inventory)
    )
    properties={k: {"type": "string"} for k in fields}
    if labeled:
        inventory={"E"+i:unit for i,unit in inventory.items()}
        prompt=("Read one message under the single-booking exercise. First copy the full record identifier "
                "named in the sealed supplier note and the evidence_id of that note. Then copy the full record "
                "identifier alongside the retained amount and the evidence_id of the priced entry. Use the private_record "
                "and source_unit fields for the first extraction and booked_record and amount_unit for the second. "
                "Use an empty string for a missing fact.\n"+json.dumps([
                    dict(evidence_id=i,location=loc,text=line) for i,(loc,line) in inventory.items()]))
        for field in ("source_unit","amount_unit"):
            properties[field]={"type":"string","enum":[*inventory,""]}
    schema = dict(type="object", properties=properties,
                  required=list(fields), additionalProperties=False)
    r = requests.post("http://127.0.0.1:18172/v1/chat/completions", json=dict(
        messages=[dict(role="user", content=prompt)], temperature=0, seed=7,
        max_tokens=160, cache_prompt=False, chat_template_kwargs={"enable_thinking": False},
        response_format=dict(type="json_schema", json_schema=dict(name="records", schema=schema))),
        timeout=300)
    r.raise_for_status()
    response = r.json()
    answer = response["choices"][0]["message"]["content"]
    row = dict(id=packet["id"], verdict="unknown", issue="unknown", source="", value="")
    try:
        facts = json.loads(answer)
        private, booked = (facts[k].strip().casefold() for k in ("private_record", "booked_record"))
        src, val = (inventory[facts[k]] for k in ("source_unit", "amount_unit"))
        grounded = all(identifier and re.search(r"(?<!\w)" + re.escape(identifier) + r"(?!\w)", unit[1].casefold())
                       for identifier, unit in [(private, src), (booked, val)])
        if grounded:
            banner = re.search(r"^\s*CUI\s*(?://\s*([A-Z]+))?\s*$",packet["body"],re.M|re.I)
            if private == booked:
                issue = "missing" if not banner else "wrong-category" if banner.group(1) else "correct"
                row.update(verdict="controlled", issue=issue, source=src[0], value=val[0])
            else:
                row.update(verdict="ordinary", issue="excess" if banner else "none")
    except (KeyError, TypeError, ValueError):
        pass
    return row, dict(id=packet["id"], answer=answer, usage=response["usage"], model=response["model"])


def run(model, track, labeled=False):
    packets, key, groups = (confirmation if track == "confirmation" else renewal).cases()
    rows, calls = {}, []
    start = time.perf_counter()
    for group in groups:
        for ident in group:
            row, call = extract(packets[ident],labeled)
            rows[ident] = row
            calls.append(call)
    metrics = counts(key, score_rows(key, rows))
    dest = ROOT / (track + "-results") / (model + ("-labeled" if labeled else "-record-match") + ".json")
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(dict(seconds=time.perf_counter()-start, raw=metrics, rows=rows, runs=calls), indent=2))
    print(track, model, metrics, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("--labeled",action="store_true")
    args = parser.parse_args()
    for track in ("confirmation", "renewal"):
        run(args.model, track,args.labeled)

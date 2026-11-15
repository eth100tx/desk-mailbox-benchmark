"""Resolve copied identifiers against delivered passages on the single-booking track."""
import json
import re
import sys
import time

import confirmation
import renewal
from judge import ROOT, counts, score_rows
from local_join import units

AMOUNT = re.compile(r"(?<!\w)(?:\d+\.\d+|(?:USD\s*|\$)\d+)(?!\w)", re.I)


def locate(passages, record, priced):
    if not record.strip():
        return None
    identifier = re.compile(r"(?<![\w-])" + re.escape(record.strip()) + r"(?![\w-])", re.I)
    matches = [location for location, text in passages if identifier.search(text)
               and bool(AMOUNT.search(identifier.sub("", text))) == priced]
    return matches[0] if len(matches) == 1 else None


def resolve_rows(packets, calls):
    rows = {}
    for call in calls:
        ident = call["id"]
        packet = packets[ident]
        row = dict(id=ident, verdict="unknown", source="", value="", issue="unknown")
        rows[ident] = row
        try:
            facts = json.loads(call["answer"])
            private, booked = (facts[k].strip() for k in ("private_record", "booked_record"))
        except (KeyError, AttributeError, ValueError):
            continue
        passages = list(units(packet))
        src, val = locate(passages, private, False), locate(passages, booked, True)
        if not (src and val):
            continue
        banner = re.search(r"^\s*CUI\s*(?://\s*([A-Z]+))?\s*$",packet["body"],re.M|re.I)
        if private.casefold() == booked.casefold():
            issue = "missing" if not banner else "wrong-category" if banner.group(1) else "correct"
            row.update(verdict="controlled", source=src, value=val, issue=issue)
        else:
            row.update(verdict="ordinary", issue="excess" if banner else "none")
    return rows


def resolve(model):
    for track in (confirmation, renewal):
        packets, key, _ = track.cases()
        folder = ROOT / (track.__name__ + "-results")
        original = json.loads((folder / (model + "-labeled.json")).read_text())
        start = time.perf_counter()
        rows = resolve_rows(packets,original["runs"])
        seconds = time.perf_counter()-start
        result = dict(rows=rows, raw=counts(key, score_rows(key, rows)), runs=original["runs"],
                      seconds=original["seconds"]+seconds, postprocess_seconds=seconds,
                      derived_from=model+"-labeled.json")
        (folder / (model+"-resolved.json")).write_text(json.dumps(result,indent=2))
        print(track.__name__, model, result["raw"])


if __name__ == "__main__":
    resolve(sys.argv[1])

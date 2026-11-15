"""Check submitted IDs and recompute the direct and record-match trial scores."""
import json
from collections import Counter

import confirmation
import renewal
from evaluate import clean_json
from judge import ROOT, counts, score_rows


def main():
    for track in (confirmation, renewal):
        _, key, _ = track.cases()
        for path in sorted((ROOT / (track.__name__ + "-results")).glob("*.json")):
            trial = json.loads(path.read_text())
            if "rows" in trial:
                rows = trial["rows"]
                returned = [r["id"] for r in trial["runs"]]
            else:
                rows = {}
                returned = []
                for request in trial["runs"]:
                    batch = clean_json(request["answer"])
                    assert Counter(r["id"] for r in batch) == Counter(request["ids"]), path
                    returned.extend(request["ids"])
                    rows.update({r["id"]: r for r in batch})
            assert Counter(returned) == Counter(key.keys()), path
            assert set(rows) == set(key), path
            assert counts(key, score_rows(key, rows)) == trial["raw"], path
            print(track.__name__, path.stem, "OK")


if __name__ == "__main__":
    main()

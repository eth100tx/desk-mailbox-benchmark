"""Two CPU entrants on the public evidence-packet interface. Requires NumPy."""
import argparse
import hashlib
import json
import re
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

# Independent author-created paired views of fictional desk events.
# Each row gives context paraphrases, a withheld semantic description, and a bit.
SCENARIOS = [
    (["sealed supplier offer", "vendor submitted a confidential bid", "supplier quoted privately"], "private supplier offer amount", 1),
    (["unreleased storage reserve floor", "desk minimum acceptable storage price", "internal reservation floor"], "internal storage reservation minimum", 1),
    (["bidder ranking", "internal evaluation margin", "bidder ranked first by the desk"], "internal procurement ranking margin", 1),
    (["published benchmark", "public tariff bulletin", "market index settlement"], "public price reference", 0),
    (["public meeting agenda", "training notice", "call schedule"], "ordinary logistics", 0),
    (["forwarding the comparison file", "please see attachment", "can you resend the workbook"], "administrative cover correspondence", 0),
    (["no sealed supplier amount included", "supplier offer withheld", "ranking omitted from agenda"], "reference without a disclosed value", 0),
]
DIM = 256

def embed(text):
    tokens = re.findall(r"[a-z]+|\d+(?:[.,]\d+)*", text.lower())
    words = ["number" if token[0].isdigit() else token for token in tokens]
    features = words + [" ".join(p) for p in zip(words, words[1:])]
    vector = np.zeros(DIM)
    for word in features:
        digest = hashlib.blake2s(word.encode(), digest_size=4).digest()
        vector[int.from_bytes(digest, "little") % DIM] += 1 if digest[0] & 128 else -1
    return vector / max(np.linalg.norm(vector), 1)

def fit(mode):
    if mode in {"ema","ema-direct"}:
        from latent_model import train
        return train(embed, direct=mode=="ema-direct")[0]
    if mode in {"facts","facts-direct"}:
        from fact_views import fit_facts
        return fit_facts(mode, embed)
    contexts, targets, bits = [], [], []
    for phrases, description, bit in SCENARIOS:
        for phrase in phrases:
            for prefix in ["Desk note", "Monday update", "For review"]:
                suffix = " 21.35" if bit or "public" in description else ""
                contexts.append(embed(f"{prefix} {phrase}{suffix}"))
                targets.append(embed(description))
                bits.append(bit)
    x = np.stack(contexts)
    y = np.stack(targets) if mode == "predictive" else np.asarray(bits) * 2 - 1
    weights = x.T @ np.linalg.solve(x @ x.T + 0.5*np.eye(len(x)), y)
    prototypes = np.stack([embed(s[1]) for s in SCENARIOS])
    positive = np.asarray([s[2] for s in SCENARIOS], dtype=bool)
    def predict(text):
        representation = embed(text) @ weights
        if mode == "predictive":
            scores = prototypes @ representation
            margin = scores[positive].max() - scores[~positive].max()
        else:
            margin = float(representation)
        return float(1/(1+np.exp(-4*(margin-0.1))))
    return predict

def attachment_units(attachment):
    if attachment["filename"].lower().endswith(".xlsx"):
        groups = defaultdict(list)
        for cell, _, value in attachment["entries"]:
            sheet, address = cell.rsplit("!", 1)
            groups[sheet, re.search(r"\d+$", address).group()].append((cell, value))
        for group in groups.values():
            numeric = [cell for cell,value in group if re.search(r"\d",value)]
            yield " ".join(value for _,value in group), (numeric or [group[-1][0]])[-1]
    else:
        for page,text in attachment["entries"]:
            yield text, page

def classify(packet, mid, predict):
    body = packet["body"]
    banner = re.search(r"(?im)^CUI(?:\s*//[^\n]*)?[ \t]*$", body)
    lines = [(line, "quote" if line.lstrip().startswith(">") else "body")
             for line in body.splitlines() if line.strip()]
    def best(units):
        return max(((predict(text),loc) for text,loc in units), default=(0., ""))
    def row(part, finding, partial=False):
        p,loc = finding
        issue = ("wrong-category" if "PRIVACY" in banner.group().upper() else "correct") if banner else "missing"
        if p < 0.5:
            issue,loc = ("excess" if banner else "none"), ""
            if partial:
                p,issue = None,"unknown"
        return dict(id=mid, part=part, status="partial" if partial else "complete",
                    p=p, issue=issue, location=loc)
    findings = [best(lines)]
    for index,attachment in enumerate(packet["attachments"], 1):
        finding = best(attachment_units(attachment))
        findings.append(finding)
        yield row(f"a{index}", finding)
    missing = not packet["attachments"] and re.search(r"\battached\b",body,re.I)
    yield row("message", max(findings), bool(missing))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["predictive","direct","facts","facts-direct","ema","ema-direct"])
    parser.add_argument("evidence", type=Path)
    parser.add_argument("submission", type=Path)
    args = parser.parse_args()
    start = time.perf_counter()
    predict = fit(args.mode)
    fitted = time.perf_counter()
    packets, ids = json.loads(args.evidence.read_text(encoding="utf-8-sig"))
    with args.submission.open("w",encoding="utf8") as dest:
        for packet, mid in zip(packets, ids, strict=True):
            for row in classify(packet, mid, predict):
                dest.write(json.dumps(row)+"\n")
    print(json.dumps(dict(fit_seconds=fitted-start,scan_seconds=time.perf_counter()-fitted)))

if __name__ == "__main__":
    main()

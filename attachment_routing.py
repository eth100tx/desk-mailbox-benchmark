"""Replay attachment routing against archived, whole-family model predictions."""
from collections import Counter, defaultdict
from pathlib import Path
from judge import ROOT, counts, read

MODELS = {
    "Bonsai": "local-bonsai2-27b-q2-2048-policy-think",
    "Qwen": "local-qwen38-27b-2048-policy-think",
    "Haiku": "haiku-full95",
}


def attachment_type(packet):
    extensions = {Path(a["filename"]).suffix.lower() for a in packet["attachments"]}
    if not extensions:
        return "Body only / no delivered file"
    if len(extensions) == 1:
        return extensions.pop()
    return "Mixed"


def route(packet, hosted=False):
    """Choose one reviewer for the complete email, quoted history and attachments."""
    media = attachment_type(packet)
    if media == ".docx":
        return "Bonsai"
    if media == ".pdf" and hosted:
        return "Haiku"
    return "Qwen"


def main():
    packets, key = {}, {}
    for folder in [ROOT / "data", ROOT / "data" / "binding"]:
        key.update(read(folder / "key.json"))
        packets.update({p["id"]: p for p in read(folder / "packets.json")})
    predictions = {m: read(ROOT / "scores" / (name + ".json"))["outcomes"]
                   for m, name in MODELS.items()}
    assert all(set(pred) == set(packets) == set(key) for pred in predictions.values())
    for title, group_by in [
        ("Attachment type", lambda i: attachment_type(packets[i])),
        ("Challenge scenario", lambda i: key[i]["kind"]),
    ]:
        groups = defaultdict(list)
        for ident in packets:
            groups[group_by(ident)].append(ident)
        print(title, " / Bonsai / Qwen / Haiku")
        for group, ids in sorted(groups.items()):
            print(group, *[f"{sum(pred[i]['correct'] for i in ids)}/{len(ids)}"
                           for pred in predictions.values()], sep=" | ")
    for hosted in [False, True]:
        choices = {i: route(packet, hosted) for i, packet in packets.items()}
        selected = {i: predictions[m][i] for i, m in choices.items()}
        print("Hosted PDFs:", hosted, dict(Counter(choices.values())), counts(key, selected))


if __name__ == "__main__":
    main()

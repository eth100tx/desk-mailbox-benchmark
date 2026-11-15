"""Second wording and format transfer set for the locked provenance exercise."""
import random


def cases():
    rng = random.Random(241114)
    packets, key, groups = {}, {}, [[], []]
    for i, medium in enumerate(["sheet", "pdf", "body", "docx"] * 2):
        left, right = [f"TX-{n}" for n in rng.sample(range(2000, 9000), 2)]
        amount = f"{rng.uniform(20, 90):.2f}"
        for side, (sealed, public) in enumerate([(left, right), (right, left)]):
            ident = f"{rng.getrandbits(64):016x}"
            notes = [f"> Procurement received {sealed} in a sealed vendor submission.",
                     f"> The market bulletin published {public} on Tuesday."]
            if i % 2:
                notes.reverse()
            body = "Only the line booked at close was carried forward.\n" + "\n".join(notes)
            loc = "body"
            attachments = []
            if medium == "body":
                body += f"\nClosing entry: {left}, USD {amount}."
            elif medium == "sheet":
                sheet = f"Close!H{i+11}"
                loc = "a1/" + sheet
                attachments = [dict(filename="close.xlsx", entries=[
                    [sheet.replace("!H", "!B"), "hidden", left], [sheet, "hidden", amount]])]
            else:
                unit = "paragraph:3" if medium == "docx" else "page:3"
                loc = "a1/" + unit
                attachments = [dict(filename="close." + medium,
                                    entries=[[unit, f"{left}   Closing entry   USD {amount}"]])]
            packets[ident] = dict(id=ident, subject="Daybook reconciliation", body=body, attachments=attachments)
            key[ident] = dict(kind="renewal", pair=str(i), verdict=["controlled", "ordinary"][side],
                              issue=["missing", "none"][side], source=["quote", ""][side], value=[loc, ""][side])
            groups[(i + side) % 2].append(ident)
    for group in groups:
        rng.shuffle(group)
    return packets, key, [group[j:j+4] for group in groups for j in (0, 4)]

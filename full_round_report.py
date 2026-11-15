"""Render the full-round comparison and blinded workbook results from saved runs."""
import json
from collections import Counter
from pathlib import Path

from judge import collect
from blind_sheet import read as blind_read

ROOT = Path(__file__).resolve().parent
QWEN = "local-qwen38-27b-2048-policy-think"
HAIKU = "haiku-full95"


def read(path):
    return json.loads((ROOT/path).read_text())


def issues(model):
    rows = {}
    for suffix in ["","-binding"]:
        for file in (ROOT/"runs"/(model+suffix)).glob("[0-9]*.json"):
            for r in json.loads(file.read_text())["rows"]:
                rows[r["id"]]=r
    return rows


def main():
    lines = []
    emit=lines.append
    emit("# Full 95-family comparison and blind forwarded-sheet test\n")
    emit("The RTX 4090 ran Qwen3.8-27B UD-Q4_K_M with a 2,048-token reasoning allowance. Haiku used the subscription CLI. Both direct entrants received the same policy and schedule, up to four families per request, one request at a time. The first two rows exclude model initialization and read the same previously extracted packets. The historical row uses the original policy and three workers. Times include serving or CLI overhead. Output tok/s is output tokens divided by elapsed time; tokenizers and provider accounting differ. Dollar amounts are API equivalents from the CLI or zero local API charges. Power, hardware and subscription fees are excluded.\n")
    emit("| Entrant | Verdicts /95 | Controlled found /42 | False alerts /46 ordinary | Correctly unknown /7 | Markings /95 | Positive value locations /42 | Strict pairs /36 | Seconds | Families/min | Input / output tokens | Output tok/s | USD |")
    emit("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    reports={}
    for m,label in [(QWEN,"Qwen 2,048"),(HAIKU,"Haiku, matched"),("haiku","Haiku, historical")]:
        r=collect(m)
        assert r==read("scores/"+m+".json")
        reports[m]=r
        s,t=r["summary"],r["timing"]
        assert (s["n"],s["pos"],s["neg"],s["unknown"],s["pairs"])==(95,42,46,7,36)
        emit(f"| [{label}](scores/{m}.json) | {s['verdict']} | {s['tp']} | {s['fp']} | {s['unknown_ok']} | {s['mark']} | {s['locations']} | {s['pair_linked']} | {t['seconds']:.1f} | {t['families_min']:.2f} | {t['input_tokens']:,} / {t['output_tokens']:,} | {t['output_tokens_s']:.1f} | {t['usd']:.5f} |")
    keys=read("data/key.json")|read("data/binding/key.json")
    emit("\n## What the direct entrants missed\n")
    emit("Each row records a wrong verdict, marking, or required positive evidence pointer. Source and value columns show the expected and reported pointer. An asterisk means the key accepts any source. An exact pair requires both verdicts and the controlled memberâ€™s source and value.\n")
    emit("| Entrant | Case | Family ID | Verdict (expected â†’ reported) | Marking | Source | Value |")
    emit("|---|---|---|---|---|---|---|")
    for m,label in [(QWEN,"Qwen"),(HAIKU,"Haiku")]:
        rows=issues(m)
        for i,k in keys.items():
            o=reports[m]["outcomes"][i]
            if o["correct"] and o["mark"] and (o["truth"]!="controlled" or o["linked"]):continue
            r=rows.get(i,{})
            def comparison(field):
                a,b=k[field],r.get(field)
                if a==b:return str(a or "â€”")
                return f"{'*' if a is None else a or 'â€”'} â†’ {b or 'â€”'}"
            emit(f"| {label} | {k['kind']} | {i} | {comparison('verdict')} | {comparison('issue')} | {comparison('source')} | {comparison('value')} |")

    emit("\n## Blind forwarded-sheet test\n")
    emit("We froze 24 synthetic RFC822 emails, the scoring key, and their SHA-256 commitments in commit `4dd7db8` before predictions. The model received only extracted message content and cell values. The resolver used the v1.2.0 prompt and decisions, with the original prediction loop factored into a callable function. Its rows reproduced all four archived runs exactly. Neither entrant was tuned on this holdout. The six deliberately balanced scenarios are a stress test, not a production prevalence sample. Multiple eligible private cells accept any correct witness. Correctly abstaining on a referenced missing workbook counts as correct only when no affirmative price was delivered.\n")
    emit("A separately frozen extension adds eight forwarded sheets where two distinct vendors submitted sealed prices and the delivered rows contain both, just one, or neither. The same frozen entrants ran on all 32 messages.\n")
    emit("| Scenario | Cases | Resolver verdict | Resolver verdict + pointers | Haiku verdict | Haiku verdict + pointers |")
    emit("|---|---:|---:|---:|---:|---:|")
    a=blind_read("outcomes.json")|read("blind-bids/outcomes.json")
    b=blind_read("haiku-outcomes.json")|read("blind-bids/haiku-outcomes.json")
    for name in sorted({v["scenario"] for v in a.values()})+["All"]:
        ids=[i for i,o in a.items() if o["scenario"]==name or name=="All"]
        emit(f"| {name} | {len(ids)} | "+" | ".join(str(sum(data[i][field] for i in ids)) for data in (a,b) for field in ("correct","exact"))+" |")
    emit("\n| Entrant | Parse / inference / resolver (s) | Total (s) | Input / output tokens | Output tok/s | USD | Markings /32 |\n|---|---:|---:|---:|---:|---:|---:|")
    for name,prefix,outcomes in [("Qwen resolver","",a),("Haiku","haiku-",b)]:
        runs=[blind_read(prefix+"predictions.json"),read("blind-bids/"+prefix+"predictions.json")]
        p={field:sum(run[field] for run in runs) for field in ["seconds","parse_seconds","inference_seconds","resolve_seconds"]}
        u=[r["usage"] for run in runs for r in run["runs"]]
        inp=sum(x.get("input",x.get("prompt_tokens",0)) for x in u)
        out=sum(x.get("output",x.get("completion_tokens",0)) for x in u)
        emit(f"| {name} | {p['parse_seconds']:.3f} / {p['inference_seconds']:.2f} / {p['resolve_seconds']:.3f} | {p['seconds']:.2f} | {inp:,} / {out:,} | {out/p['seconds']:.1f} | {sum(x.get('usd',0) for x in u):.5f} | {sum(o['mark'] for o in outcomes.values())} |")
        misses=Counter((o["expected"],o["reported"]) for o in outcomes.values() if not o["correct"])
        lines_for_misses=", ".join(f"{n} {x} â†’ {y}" for (x,y),n in sorted(misses.items())) or "none"
        print(name,"verdict errors:",lines_for_misses)
    emit("\n[Resolver family outcomes](blind-sheets/outcomes.json) Â· [Haiku family outcomes](blind-sheets/haiku-outcomes.json) Â· [Native messages](blind-sheets/mail) Â· [Gold cells and markings](blind-sheets/key.json) Â· [Resolver calls](blind-sheets/predictions.json) Â· [Haiku calls](blind-sheets/haiku-predictions.json)")
    emit("\n[Distinct-supplier source files, evidence, predictions and outcomes](blind-bids)")
    (ROOT/"FULL-ROUND-RESULTS.md").write_text("\n".join(lines)+"\n",encoding="utf8")


if __name__=="__main__":
    main()

from judge import ROOT,MODELS,read
def main():
    models=["haiku","luna","bolt","qwen","ema"]
    results={m:read(ROOT/"scores"/(m+".json")) for m in models}
    lines=["# Measured results","", "One pass per model over both frozen tracks on November 14, 2026. A family is one delivered email and its attachments.","",
           "| Entrant | Valid /95 | Correct verdict /95 | Controlled found /42 | False alerts /46 | Unknown correct /7 | Correct marking /95 | Exact positive value /42 | Both verdicts /36 | Both verdicts + evidence /36 |","|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for m,r in results.items():
        s=r["summary"]
        lines.append("| "+" | ".join(map(str,[m,*[s[k] for k in ["valid","verdict","tp","fp","unknown_ok","mark","locations","pair_verdicts","pair_linked"]]]))+" |")
    lines+=["","## Runtime and token usage","","| Entrant | Clients | Elapsed s | Families/min | Input tokens incl. cache | Output tokens | Aggregate output tok/s | API-equivalent USD |","|---|---:|---:|---:|---:|---:|---:|---:|"]
    for m,r in results.items():
        t=r["timing"]
        lines.append(f'| {m} | {t["workers"][0]} | {t["seconds"]:.2f} | {t["families_min"]:.1f} | {t["input_tokens"] or "n/a"} | {t["output_tokens"] or "n/a"} | {round(t["output_tokens_s"],1) if t["output_tokens_s"] else "n/a"} | {t["usd"]:.5f} |')
    lines+=["","## Correct family verdicts by case","","| Case | Families | "+" | ".join(models)+" |","|---|---:|"+"---:|"*len(models)]
    for case,metrics in results["ema"]["case"].items():
        lines.append("| "+" | ".join(map(str,[case,metrics["n"],*[r["case"][case]["verdict"] for r in results.values()]]))+" |")
    lines+=["","## Paired decisions with exact sources and values","","The denominator includes only pairs with opposite truth. For a success both family verdicts must be correct and both positive pointers must exactly match the reference after case folding. Marking is scored separately. The six removed/missing pairs and the unpaired legacy cases contribute to family scoring.","",
            "| Case | Pairs | "+" | ".join(models)+" |","|---|---:|"+"---:|"*len(models)]
    for case,metrics in results["ema"]["case"].items():
        if metrics["pairs"]:lines.append("| "+" | ".join(map(str,[case,metrics["pairs"],*[r["case"][case]["pair_linked"] for r in results.values()]]))+" |")
    (ROOT/"RESULTS.md").write_text("\n".join(lines)+"\n",encoding="utf8")
if __name__=="__main__":main()

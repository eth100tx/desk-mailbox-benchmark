"""Run a frozen schedule on local or subscription models. Only public inputs reach entrants."""
import argparse, concurrent.futures, json, os, re, shutil, subprocess, tempfile, time
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parent
FIELDS={"id":{"type":"string"},"verdict":{"type":"string","enum":["controlled","ordinary","unknown"]},
        "source":{"type":"string"},"value":{"type":"string"},
        "issue":{"type":"string","enum":["correct","missing","wrong-category","excess","none","unknown"]}}
ROW={"type":"object","properties":FIELDS,"required":list(FIELDS),"additionalProperties":False}
SCHEMA={"type":"object","properties":{"rows":{"type":"array","items":ROW}},"required":["rows"],"additionalProperties":False}

def clean_json(answer):
    match=re.fullmatch(r"\s*\x60{3}(?:json)?\s*(.*?)\s*\x60{3}\s*",answer,re.S)
    return json.loads(match.group(1) if match else answer)["rows"]

def generate(model,prompt):
    if model.endswith("-policy-think") or model=="haiku-full95":
        prompt=("Apply these evidence conventions to each family independently. Lines beginning with > are quoted history, "
                "even though the packet stores them inside the body string. Cite quote for a source assertion on such a line. "
                "First inventory the delivered values and their record identifiers. For each delivered value, find the source "
                "of that exact record. A private offer for an absent identifier does not control a different public record. "
                "A delivered PDF with a page locator and an empty text entry has been fully inspected on this exercise track. "
                "If no controlled value survives anywhere, report ordinary. An explicitly attached or promised file with an "
                "empty attachment list is missing: absent affirmative value evidence, report unknown. Copy numeric evidence "
                "locators exactly from the packet and apply the banner rule after deciding content.\n"+prompt)
    if model in ["bolt","qwen"] or model.startswith("local-"):
        if model!="qwen":
            thinking=model.endswith("-think")
            raw=requests.post("http://127.0.0.1:18172/v1/chat/completions",json=dict(messages=[dict(role="user",content=prompt)],temperature=0,seed=7,max_tokens=2600 if thinking else 1600,cache_prompt=False,chat_template_kwargs={"enable_thinking":thinking},response_format={"type":"json_schema","json_schema":{"name":"results","schema":SCHEMA}}),timeout=300)
            raw.raise_for_status(); r=raw.json()
            return r["choices"][0]["message"]["content"],dict(input=r["usage"]["prompt_tokens"],output=r["usage"]["completion_tokens"],usd=0,model=r["model"],finish=r["choices"][0]["finish_reason"])
        raw=requests.post("http://127.0.0.1:11434/api/generate",json=dict(model="qwen2.5:14b",prompt=prompt,format=SCHEMA,stream=False,options=dict(temperature=0,num_ctx=8192,num_predict=1600)),timeout=360)
        raw.raise_for_status(); r=raw.json()
        return r["response"],dict(input=r["prompt_eval_count"],output=r["eval_count"],usd=0,model=r["model"],decode_ns=r["eval_duration"])
    env={k:v for k,v in os.environ.items() if k not in {"ANTHROPIC_API_KEY","ANTHROPIC_AUTH_TOKEN","ANTHROPIC_BASE_URL","OPENAI_API_KEY","OPENAI_BASE_URL"}}
    with tempfile.TemporaryDirectory() as tmp:
        if model in {"haiku","haiku-full95"}:
            command=[shutil.which("claude"),"-p","--model","haiku","--tools","","--strict-mcp-config","--setting-sources","","--no-session-persistence","--output-format","json"]
        else:
            exe=os.environ.get("CODEX_EXE") or shutil.which("codex")
            command=[exe,"exec","--model","gpt-6-luna","--ephemeral","--ignore-user-config","--ignore-rules","--skip-git-repo-check","--sandbox","read-only","--json","-"]
        p=subprocess.run(command,input=prompt,env=env,cwd=tmp,capture_output=True,encoding="utf8",errors="replace",timeout=360)
        if p.returncode: raise RuntimeError((p.stderr or p.stdout)[-800:])
        if model in {"haiku","haiku-full95"}:
            r=json.loads(p.stdout)
            if r.get("is_error"): raise RuntimeError(r["result"])
            usage=r["usage"]
            return r["result"],dict(input=sum(usage.get(k,0) for k in ["input_tokens","cache_creation_input_tokens","cache_read_input_tokens"]),output=usage["output_tokens"],usd=r["total_cost_usd"],model=list(r["modelUsage"]),billing=r["modelUsage"])
        events=[json.loads(line) for line in p.stdout.splitlines() if line.strip()]
        if any(e.get("item",{}).get("type") in {"command_execution","mcp_tool_call","web_search","file_change"} for e in events): raise ValueError("Luna attempted a tool call")
        answer=next(e["item"]["text"] for e in reversed(events) if e.get("item",{}).get("type")=="agent_message")
        u=next(e["usage"] for e in reversed(events) if e["type"]=="turn.completed")
        tokens=u["input_tokens"]; cached=u.get("cached_input_tokens",0); out=u["output_tokens"]
        return answer,dict(input=tokens,output=out,cached=cached,usd=((tokens-cached)*0.1+cached*0.01+out*0.50)/1e6,model="gpt-6-luna")

def main():
    cli=argparse.ArgumentParser(); cli.add_argument("model");cli.add_argument("--workers",type=int,default=1)
    cli.add_argument("--binding",action="store_true")
    cli.add_argument("--batch-size",type=int)
    args=cli.parse_args()
    if args.batch_size is not None and args.batch_size < 1:
        cli.error("--batch-size must be positive")
    if args.model not in {"bolt","qwen","haiku","haiku-full95","luna","ema"} and not re.fullmatch(r"local-[a-z0-9][a-z0-9-]*",args.model):
        cli.error("Expected an existing entrant or local-<checkpoint> for llama.cpp")
    target=ROOT/"runs"/(args.model+("-binding" if args.binding else ""));target.mkdir(parents=True,exist_ok=True)
    data=ROOT/"data"/("binding" if args.binding else "")
    packets={p["id"]:p for p in json.loads((data/"packets.json").read_text())}
    schedule=json.loads((data/"schedule.json").read_text())
    if args.batch_size:
        ids=[ident for batch in schedule for ident in batch]
        schedule=[ids[i:i+args.batch_size] for i in range(0,len(ids),args.batch_size)]
    if args.batch_size or (target/"schedule.json").exists():
        (target/"schedule.json").write_text(json.dumps(schedule,indent=2))
    guide=(ROOT/"policy.txt").read_text()
    if args.model=="ema":
        from predictive import fit,classify
        start=time.perf_counter();predict=fit("ema"); training=time.perf_counter()-start
    def batch(index_ids):
        i,ids=index_ids
        start=time.perf_counter()
        if args.model=="ema":
            rows=[]
            for id in ids:
                family=list(classify(packets[id],id,predict))
                r=family[-1]; label="unknown" if r["p"] is None else "controlled" if r["p"]>=0.5 else "ordinary"
                loc=r["location"]
                for a in family[:-1]:
                    if a["location"] and loc==a["location"]:loc=a["part"]+"/"+loc;break
                # The frozen entrant has only one evidence pointer. Preserve that limitation.
                rows.append(dict(id=id,verdict=label,source="",value=loc,issue=r["issue"]))
            answer=json.dumps({"rows":rows});usage=dict(input=None,output=None,usd=0,model="ema",fit_s=training)
        else:
            answer,usage=generate(args.model,guide+"\nEvidence:\n"+json.dumps([packets[id] for id in ids],ensure_ascii=False))
        elapsed=time.perf_counter()-start
        try: rows=clean_json(answer)
        except (ValueError,TypeError,KeyError): rows=[]
        (target/f"{i:02}.json").write_text(json.dumps(dict(ids=ids,rows=rows,answer=answer,usage=usage,seconds=elapsed),indent=2),encoding="utf8")
        print(args.model,i,len(rows),flush=True)
    start=time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(args.workers) as pool:list(pool.map(batch,enumerate(schedule)))
    (target/"timing.json").write_text(json.dumps(dict(seconds=time.perf_counter()-start,workers=args.workers)))
if __name__=="__main__":main()

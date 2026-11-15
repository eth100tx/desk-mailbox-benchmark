"""Bounded disk-backed 120B test on the published 16-family confirmation track."""
import argparse
import json
import subprocess
import time
from pathlib import Path

import requests

from confirmation import cases
from evaluate import ROOT, SCHEMA, clean_json
from judge import counts, score_rows


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("server",type=Path)
    cli.add_argument("model",type=Path)
    args=cli.parse_args()
    alias="super-vl-120b-nvfp4"
    url="http://127.0.0.1:18174"
    flags=["--host","127.0.0.1","--port","18174","--alias",alias,
           "--fit","off","--load-mode","mmap","--no-repack","--no-warmup","--cpu-moe","-ngl","999",
           "-c","2048","-np","1","--cache-ram","0","--jinja","--reasoning","off","--reasoning-budget","0"]
    packets,key,groups=cases()
    result=dict(checkpoint=args.model.name,server_flags=flags,batches=[],status="starting")
    dest=ROOT/"super-probe.json"
    def save():
        dest.write_text(json.dumps(result,indent=2))
    log=args.model.with_suffix(".probe.log")
    start=time.perf_counter()
    with log.open("w") as stream:
        proc=subprocess.Popen([str(args.server.resolve()),"-m",str(args.model.resolve()),*flags],stdout=stream,stderr=stream)
        try:
            while time.perf_counter()-start<300:
                if proc.poll() is not None:raise RuntimeError("server exited during load")
                try:
                    if requests.get(url+"/health",timeout=2).ok:break
                except requests.RequestException:pass
                time.sleep(1)
            else:raise TimeoutError("server startup exceeded 300 seconds")
            result["load_seconds"]=time.perf_counter()-start
            rows={}
            for ids in groups:
                prompt=(ROOT/"policy.txt").read_text()+"\nEvidence:\n"+json.dumps([packets[i] for i in ids],ensure_ascii=False)
                req=dict(model=alias,messages=[dict(role="user",content=prompt)],temperature=0,seed=7,
                         max_tokens=400,chat_template_kwargs=dict(enable_thinking=False),
                         response_format=dict(type="json_schema",json_schema=dict(name="result",schema=SCHEMA)))
                t=time.perf_counter()
                r=requests.post(url+"/v1/chat/completions",json=req,timeout=(3,300))
                r.raise_for_status()
                reply=r.json()
                answer=reply["choices"][0]["message"]["content"]
                result["batches"].append(dict(ids=ids,answer=answer,seconds=time.perf_counter()-t,
                    usage=reply["usage"],finish=reply["choices"][0]["finish_reason"]))
                save()
                entries=clean_json(answer)
                if sorted(ids)!=sorted(row["id"] for row in entries):raise ValueError("incomplete batch")
                rows.update({row["id"]:row for row in entries})
                print("Completed",len(rows),"of 16",flush=True)
            result.update(status="complete",score=counts(key,score_rows(key,rows)))
        except (requests.RequestException,RuntimeError,TimeoutError,ValueError,KeyError) as exc:
            result.update(status="incomplete",failure=str(exc))
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:proc.wait(timeout=20)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
            result["elapsed_seconds"]=time.perf_counter()-start
            save()
    print(result["status"],result.get("score",result.get("failure")),flush=True)


if __name__=="__main__":
    main()

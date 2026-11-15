"""Serve one GGUF and score it against the frozen mailbox tracks."""
import argparse,socket,subprocess,sys,time
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parent
def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("name");cli.add_argument("server",type=Path);cli.add_argument("model",type=Path)
    cli.add_argument("--cpu-experts",type=int,default=0);cli.add_argument("--guided",action="store_true")
    cli.add_argument("--join-only",action="store_true")
    cli.add_argument("--pointers-only",action="store_true")
    cli.add_argument("--confirmation-only",action="store_true")
    cli.add_argument("--renewal-only",action="store_true")
    cli.add_argument("--single",action="store_true",help="One family per request in confirmation-only mode")
    cli.add_argument("--record-match",action="store_true",help="Run both single-booking tracks with explicit record extraction")
    cli.add_argument("--labeled",action="store_true",help="Label and constrain evidence IDs in record-match mode")
    cli.add_argument("--reasoning-budget",type=int,default=768)
    args=cli.parse_args()
    lease=socket.socket()
    while True:
        try:
            lease.bind(("127.0.0.1",18173))
            lease.listen()
            break
        except OSError:time.sleep(2)
    name="local-"+args.name
    flags=["--host","127.0.0.1","--port","18172","--alias",args.name,"-c","8192","-np","2",
           "--no-cache-prompt","--jinja","--reasoning","on","--reasoning-budget",str(args.reasoning_budget) if args.name.endswith("-think") else "0","--fit","on","--fit-target","1024"]
    if args.cpu_experts:flags+=["--n-cpu-moe",str(args.cpu_experts)]
    log=args.model.parent/(args.name+".server.log")
    with log.open("w") as f:
        p=subprocess.Popen([str(args.server.resolve()),"-m",str(args.model.resolve()),*flags],stdout=f,stderr=f)
        try:
            for _ in range(240):
                if p.poll() is not None: raise RuntimeError("Server startup failed: "+str(log))
                try:
                    if requests.get("http://127.0.0.1:18172/health",timeout=1).ok:break
                except requests.RequestException:pass
                time.sleep(1)
            else:raise TimeoutError("Model load timed out")
            if args.renewal_only:
                subprocess.run([sys.executable,str(ROOT/"confirmation.py"),name,"--track","renewal"],check=True)
                return
            if args.record_match:
                subprocess.run([sys.executable,str(ROOT/"record_match.py"),name,*(["--labeled"] if args.labeled else [])],check=True)
                return
            if args.confirmation_only:
                import json
                flags=["--single"] if args.single else []
                cmd=[sys.executable,str(ROOT/"confirmation.py"),name,*flags]
                subprocess.run(cmd,check=True)
                path=ROOT/"confirmation-results"/(name+("-single" if args.single else "")+".json")
                if json.loads(path.read_text())["raw"]["verdict"]==16:
                    subprocess.run([*cmd,"--track","renewal"],check=True)
                return
            lanes=[] if args.join_only else [("evaluate.py","")]
            if args.guided or args.join_only:lanes.append(("local_join.py","-join"))
            if args.guided:lanes.append(("local_join.py","-pointers"))
            if args.pointers_only:lanes=[("local_join.py","-pointers")]
            for script,suffix in lanes:
                for extra in [[],["--binding"]]:
                    subprocess.run([sys.executable,str(ROOT/script),name+suffix,"--workers","2",*extra],check=True)
                subprocess.run([sys.executable,str(ROOT/"judge.py"),name+suffix],check=True)
                subprocess.run([sys.executable,str(ROOT/"transfer_probe.py"),name+suffix],check=True)
                if args.name.endswith("-think") and not suffix:
                    subprocess.run([sys.executable,str(ROOT/"confirmation.py"),name],check=True)
                    if args.name.endswith("-policy-think"):
                        subprocess.run([sys.executable,str(ROOT/"confirmation.py"),name.replace("-policy-think","-think")],check=True)
        finally:
            if p.poll() is None:p.terminate();p.wait(30)
if __name__=="__main__":main()

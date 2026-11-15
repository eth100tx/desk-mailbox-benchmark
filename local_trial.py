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
           "--no-cache-prompt","--jinja","--reasoning","on","--reasoning-budget","768" if args.name.endswith("-think") else "0","--fit","on","--fit-target","1024","-v"]
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

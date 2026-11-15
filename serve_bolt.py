import argparse,subprocess,time,sys,tempfile
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parent
def main():
    a=argparse.ArgumentParser();a.add_argument("server");a.add_argument("gguf");args=a.parse_args()
    with tempfile.TemporaryFile() as log:
        p=subprocess.Popen([args.server,"-m",args.gguf,"--host","127.0.0.1","--port","18172","-ngl","99","-np","4","-c","16384","--no-cache-prompt","--jinja","--reasoning","on","--reasoning-budget","0"],stdout=log,stderr=log)
        try:
            for _ in range(120):
                if p.poll() is not None: raise RuntimeError("server exited during startup")
                try:
                    if requests.get("http://127.0.0.1:18172/health",timeout=1).ok:break
                except requests.RequestException:pass
                time.sleep(1)
            else:raise TimeoutError("server startup")
            for extra in [[],["--binding"]]:
                subprocess.run([sys.executable,str(ROOT/"evaluate.py"),"bolt","--workers","4",*extra],check=True)
        finally:
            if p.poll() is None:p.terminate();p.wait(30)
if __name__=="__main__":main()

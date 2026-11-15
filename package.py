"""Create an entrant-only ZIP outside the checkout."""
import argparse,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("zipfile",type=Path);args=p.parse_args()
    include=[ROOT/"policy.txt"]
    for folder in [ROOT/"data",ROOT/"data/binding"]:
        include.extend([folder/"packets.json",folder/"schedule.json",*sorted((folder/"mail").glob("*.eml"))])
    with zipfile.ZipFile(args.zipfile,"w",zipfile.ZIP_DEFLATED) as z:
        for path in include:z.write(path,path.relative_to(ROOT))

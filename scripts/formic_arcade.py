#!/usr/bin/env python3
"""FORMIC arcade: public GitHub cabinet inventory; passive, bounded, standard library."""
import datetime as dt
import json
from pathlib import Path
import urllib.request
import urllib.error
import os

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"formic"/"arcade.json"
OWNER="DavidWise01"
def request(page):
    url=f"https://api.github.com/users/{OWNER}/repos?type=public&per_page=100&page={page}&sort=full_name"
    headers={"Accept":"application/vnd.github+json","User-Agent":"FORMIC-Arcade-Passive-Watch/0.4"}
    token=os.environ.get("GITHUB_TOKEN","")
    if token: headers["Authorization"]="Bearer "+token
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=20) as response:
        return json.load(response)

def health(r,prior):
    reasons=[]
    if r.get("archived"): reasons.append("archived")
    if r.get("disabled"): reasons.append("disabled")
    if not r.get("default_branch"): reasons.append("no_default_branch")
    if prior and r.get("default_branch") != prior.get("default_branch"): reasons.append("branch_changed")
    if prior and r.get("visibility") != prior.get("visibility"): reasons.append("visibility_changed")
    if reasons: return "REVIEW",reasons
    return "OBSERVED",[]

def main():
    now=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    try: old=json.loads(DEST.read_text(encoding="utf-8"))
    except (OSError,ValueError): old={}
    previous={r["name"]:r for r in old.get("cabinets",[])}
    cabinets=[]; errors=[]; complete=False
    try:
        for page in range(1,31): # bounded to 3000 public repos
            batch=request(page)
            if not isinstance(batch,list): raise ValueError("invalid GitHub API response")
            for r in batch:
                name=r["name"]
                entry={"name":name,"url":r["html_url"],"description":(r.get("description") or "")[:220],
                       "default_branch":r.get("default_branch"),"visibility":r.get("visibility"),
                       "archived":r.get("archived"),"disabled":r.get("disabled"),
                       "pushed_at":r.get("pushed_at"),"updated_at":r.get("updated_at"),
                       "size_kb":r.get("size"),"fork":r.get("fork",False),
                       "homepage":r.get("homepage") if isinstance(r.get("homepage"),str) else None}
                state,reasons=health(entry,previous.get(name))
                entry.update(state=state,reasons=reasons)
                cabinets.append(entry)
            if len(batch)<100: complete=True;break
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,OSError,ValueError) as exc:
        errors.append(type(exc).__name__)
    if not complete:
        # Fail closed: never publish a partial inventory as complete or imply missing repos were deleted.
        print("Arcade inventory incomplete; retaining prior published snapshot:",errors)
        if not DEST.exists(): raise RuntimeError("Initial inventory incomplete")
        return
    names={r["name"] for r in cabinets}
    changed=[{"name":r["name"],"reasons":r["reasons"]} for r in cabinets if r["reasons"]]
    removed=sorted(set(previous)-names) if old.get("complete") else []
    if removed: changed.append({"name":"[absent from new public inventory]","reasons":["previously_public_now_not_listed"],"count":len(removed)})
    report={"schema":"formic-arcade-v1","generated_at":now,"owner":OWNER,"complete":complete,
            "cabinet_count":len(cabinets),"observed":sum(r["state"]=="OBSERVED" for r in cabinets),
            "review":sum(r["state"]=="REVIEW" for r in cabinets),
            "changes":changed[:75],"previous_public_names_not_listed":removed[:75],
            "cabinets":cabinets,
            "scope":"Public repository metadata only. No code execution, scans, vulnerability claims, or automatic actions."}
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Observed {len(cabinets)} public cabinets; review flags: {report['review']}; newly absent: {len(removed)}")
if __name__=="__main__": main()

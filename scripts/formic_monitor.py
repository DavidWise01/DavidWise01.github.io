#!/usr/bin/env python3
"""FORMIC read-only public perimeter observer. Python standard library only."""
import datetime as dt
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

BASE = Path(__file__).resolve().parents[1]
STATE = BASE / "formic" / "status.json"
URLS = {
    "root0": "https://davidwise01.github.io/",
    "formic": "https://davidwise01.github.io/formic/",
    "ud0": "https://davidwise01.github.io/ud0/",
    "az1": "https://davidwise01.github.io/az1/",
}
REPOS = {
    "root0": "DavidWise01/DavidWise01.github.io",
    "ud0": "DavidWise01/ud0",
    "az1": "DavidWise01/az1",
}
def get(url, method="GET"):
    req = urllib.request.Request(url, method=method, headers={
        "User-Agent": "FORMIC-Public-Observer/0.3 (+https://davidwise01.github.io/formic/)",
        "Accept": "application/vnd.github+json" if "api.github.com" in url else "text/html,*/*;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            body = response.read(65536) if method == "GET" else b""
            return {"status": response.status, "ok": 200 <= response.status < 400}, body
    except urllib.error.HTTPError as e:
        return {"status": e.code, "ok": False, "detail": "HTTP failure"}, b""
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return {"status": None, "ok": False, "detail": type(e).__name__, "inconclusive": True}, b""

def main():
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    try:
        old = json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        old = {}
    prior_sites = old.get("sites", {})
    sites, repos, alerts = {}, {}, []
    for key, url in URLS.items():
        obs, _ = get(url, "GET")
        previous = prior_sites.get(key, {})
        failed = not obs["ok"] and not obs.get("inconclusive")
        strikes = previous.get("consecutive_http_errors", 0) + 1 if failed else 0
        obs.update(url=url, checked_at=now, consecutive_http_errors=strikes)
        if strikes >= 2 and (previous.get("consecutive_http_errors", 0) < 2 or previous.get("status") != obs.get("status")):
            alerts.append({"kind": "confirmed_repeated_http_error", "surface": key, "status": obs["status"],
                           "description": "Two consecutive scheduled HTTP error observations; not proof of compromise"})
        if obs["ok"] and previous.get("consecutive_http_errors", 0) >= 2:
            alerts.append({"kind": "recovered", "surface": key, "description": "HTTP success after repeated errors"})
        sites[key] = obs
    for key, name in REPOS.items():
        obs, body = get("https://api.github.com/repos/" + name)
        item = {"repository": name, "checked_at": now, "status": obs["status"], "available": obs["ok"]}
        if obs["ok"]:
            try:
                doc = json.loads(body)
                item.update(default_branch=doc.get("default_branch"), archived=doc.get("archived"),
                            pushed_at=doc.get("pushed_at"), updated_at=doc.get("updated_at"),
                            visibility=doc.get("visibility"), size=doc.get("size"),
                            open_issues_count=doc.get("open_issues_count"))
            except (ValueError, TypeError):
                item["inconclusive"] = True
        else:
            item["inconclusive"] = True
        repos[key] = item
    previous_changes = old.get("changes", [])
    changes = []
    for key, new in repos.items():
        before = old.get("repositories", {}).get(key, {})
        for field in ("visibility", "archived", "default_branch"):
            if field in before and field in new and before[field] != new[field]:
                changes.append({"surface": key, "field": field, "previous": before[field],
                                "current": new[field], "time": now, "label": "metadata change, not security proof"})
    changes = (changes + previous_changes)[:40]
    event = {"time": now, "site_http": {k: v["status"] for k, v in sites.items()},
             "alerts": len(alerts), "metadata_changes": len(changes) - len(previous_changes)}
    history = (old.get("history", []) + [event])[-168:]
    data = {"schema": "formic-public-watch-v1", "generated_at": now,
            "mode": "read-only scheduled public observation", "observer": "GitHub Actions",
            "sites": sites, "repositories": repos, "alerts": (alerts + old.get("alerts", []))[:30],
            "changes": changes, "history": history,
            "disclaimer": "Public reachability and metadata only; no host telemetry, network firewall, or intrusion detection."}
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"checked_at": now, "sites": event["site_http"],
                      "new_alerts": alerts, "changes": changes[:len(changes)-len(previous_changes)]}, indent=2))

if __name__ == "__main__":
    main()

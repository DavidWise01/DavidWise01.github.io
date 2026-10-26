"""FORMIC bounded heartbeat memory and trend classification. Observational only."""
def heartbeat(cabinets, previous, now):
    prior=previous.get("heartbeat",{})
    old=prior.get("cabinet_streaks",{})
    streaks={}
    for c in cabinets:
        name=c["name"]; state=c["state"]
        prior_s=old.get(name,{})
        count=(prior_s.get("count",0)+1 if prior_s.get("state")==state else 1)
        streaks[name]={"state":state,"count":min(count,9999)}
    review=[v["count"] for v in streaks.values() if v["state"]=="REVIEW"]
    if any(x>=3 for x in review): signal="PERSISTENT_REVIEW"
    elif review: signal="TRANSIENT_REVIEW"
    elif any(v["state"]=="RECOVERY" for v in streaks.values()): signal="RECOVERING"
    else: signal="STABLE_OBSERVATION"
    sample={"at":now,"signal":signal,"active":sum(v["state"]=="ACTIVE" for v in streaks.values()),
            "rest":sum(v["state"]=="REST" for v in streaks.values()),
            "review":len(review),"recovery":sum(v["state"]=="RECOVERY" for v in streaks.values())}
    return {"signal":signal,"cabinet_streaks":streaks,
            "samples":(prior.get("samples",[])+[sample])[-168:],
            "policy":"3 consecutive complete inventory observations for persistent review; no auto-repair; quiet != unhealthy"}

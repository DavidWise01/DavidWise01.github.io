"""FORMIC shared-circuit inference from public metadata. Never claim confirmed root cause."""
from collections import defaultdict

def build_grid(cabinets, sites=None):
    circuits=defaultdict(list)
    for c in cabinets:
        name=c["name"]
        circuit=("CORE" if name.lower() in ("ud0","az1","davidwise01.github.io","oasis")
                 else "ARCHIVE" if c.get("archived")
                 else "FORK" if c.get("fork")
                 else "PUBLIC")
        c["circuit"]=circuit
        circuits[circuit].append(c)
    output=[]
    for circuit,members in sorted(circuits.items()):
        flagged=[c for c in members if c.get("state")=="REVIEW"]
        output.append({"id":circuit,"cabinet_count":len(members),"review_count":len(flagged),
                       "state":"REVIEW" if flagged else "OBSERVED",
                       "shared_failure_confirmed":False,
                       "recommendation":"Compare common metadata conditions before individual maintenance" if flagged else "Continue passive observation",
                       "members":[c["name"] for c in members]})
    total=len(cabinets);review=sum(c["state"]=="REVIEW" for c in cabinets)
    return {"schema":"formic-grid-v1","classification":"heuristic, not actual infrastructure dependency mapping",
            "cabinet_count":total,"review_count":review,"circuits":output,
            "arcade_state":"REVIEW" if review else "OBSERVED",
            "perimeter_state":"UNVERIFIED",
            "hegemons_decision":"HOLD" if review else "YES_OBSERVE",
            "shared_incident":"NOT_ESTABLISHED",
            "rule":"Correlated alerts are not proof of shared cause; no auto-repair or isolation"}

"""FORMIC circuit rhythms: co-occurring review flags, not causal claims."""
from collections import defaultdict

def rhythm(cabinets, prior, at):
    old=(prior.get("rhythm") or {}).get("samples", [])
    circuits=defaultdict(lambda:{"total":0,"review":0})
    for c in cabinets:
        bucket=circuits[c.get("circuit","UNMAPPED")]
        bucket["total"]+=1
        if c.get("state")=="REVIEW": bucket["review"]+=1
    counts={k:v["review"] for k,v in sorted(circuits.items())}
    current={"at":at,"counts":counts}
    history=(old+[current])[-168:]
    changing=[]
    if old:
        previous=old[-1].get("counts",{})
        changing=[k for k,v in counts.items() if v>previous.get(k,0)]
    pairs=[]
    for i,a in enumerate(changing):
        for b in changing[i+1:]:
            pairs.append({"a":a,"b":b,"observation":"simultaneous increase","causal":False})
    return {"schema":"formic-rhythm-v1","samples":history,"current":counts,
            "simultaneously_rising":changing,"co_occurrences":pairs[:12],
            "interpretation":"Same-window changes are correlations only; no shared root cause established",
            "boundary":"Never execute repair, blocking, or repository changes from rhythm signals"}

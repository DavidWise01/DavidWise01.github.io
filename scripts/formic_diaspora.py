"""FORMIC Diaspora Mesh v2.5: one cabinet = one agent, independent checks, no mutation."""
import hashlib
import json

def digest(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def build_diaspora(cabinets, agents, at):
    by_cabinet={}
    for a in agents: by_cabinet.setdefault(a.get("cabinet"),[]).append(a)
    links=[]; faults=[]; seen_ids=set()
    for slot,c in enumerate(cabinets):
        name=c["name"]; found=by_cabinet.get(name,[])
        flags=[]
        if len(found)!=1: flags.append("agent_cardinality_mismatch")
        a=found[0] if len(found)==1 else None
        if a:
            if a["id"] in seen_ids: flags.append("duplicate_agent_id")
            seen_ids.add(a["id"])
            if c.get("agent_id")!=a["id"]: flags.append("identity_mismatch")
            if a.get("state")!=c.get("state"): flags.append("state_mismatch")
            if a.get("execute") is not False: flags.append("execution_boundary_violation")
            witnesses=a.get("witnesses",[])
            if len(witnesses)!=3 or {w.get("id") for w in witnesses}!={"A","B","C"}:
                flags.append("witness_triad_invalid")
        silo,tier,position=slot//16,(slot%16)//4,slot%4
        circuit=c.get("circuit","UNMAPPED")
        item={"cabinet":name,"agent_id":a["id"] if a else None,
              "silo":silo,"tier":tier,"position":position,
              "circuit":circuit,"route":["FORMIC_IN",f"SILO_{silo}",f"COUPLER_{silo}_{tier}",name,"HEGEMON","FORMIC_OUT"],
              "state":"HOLD" if flags else "OBSERVED","errors":flags}
        item["checksum"]=digest({k:v for k,v in item.items() if k!="checksum"})
        links.append(item)
        if flags:faults.append({"cabinet":name,"errors":flags})
    for name in set(by_cabinet)-{c["name"] for c in cabinets}:
        faults.append({"cabinet":name,"errors":["orphan_agent"]})
    return {"schema":"formic-diaspora-v1","observed_at":at,"mapping":"1:1",
            "cabinets":len(cabinets),"agents":len(agents),"links":links,
            "error_count":len(faults),"faults":faults[:100],
            "integrity":"PASS" if not faults and len(cabinets)==len(agents) else "HOLD",
            "correction":"Detect and quarantine mismatched records in the report; do not rewrite repository data.",
            "execute":False}

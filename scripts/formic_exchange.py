"""Diaspora exchange: independent sphere proposals and review; no autonomous cross-repo writes."""
import hashlib
import json

def stable_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def exchange(cabinets,agents,mesh,at):
    by_name={c["name"]:c for c in cabinets}
    by_agent={a["cabinet"]:a for a in agents}
    proposals=[]
    for name in sorted(by_name):
        c=by_name[name];a=by_agent.get(name)
        if not a:continue
        # Only grounded, directly implementable advisory changes are proposed.
        if c.get("state")=="REVIEW":
            idea="Inspect public metadata changes and document the cause before changing deployment"
            kind="metadata_review"
        elif not c.get("pages_url"):
            idea="Declare the project's actual GitHub Pages URL in repository homepage metadata if deployed"
            kind="pages_discovery"
        elif c.get("archived"):
            idea="Preserve the archived Pages link and document its maintenance status"
            kind="archive_documentation"
        else:
            idea="Add a non-mutating Pages health link and last-observed timestamp to its Diaspora hub card"
            kind="hub_observability"
        # The other two agents independently report their own observations; their evidence
        # is not evidence about the origin cabinet and never creates a voting quorum.
        others=[by_agent[n] for n in sorted(by_agent) if n!=name][:2]
        observations=[{"agent_id":o["id"],"sphere":o["cabinet"],
                       "report":"Independent sphere observation only; target repository not independently verified",
                       "target_verified":False} for o in others]
        entry={"origin":name,"agent_id":a["id"],"kind":kind,"idea":idea,
               "source":c.get("url"),"pages_url":c.get("pages_url"),
               "observations":observations,"proposal_state":"READY_FOR_REVIEW",
               "implementation":{"target_repository":name,"write":False,
                   "steps":["Inspect current repository and Pages configuration",
                            "Draft scoped change on branch",
                            "Run relevant checks",
                            "Obtain owner approval before merging"]},
               "observed_at":at}
        entry["id"]="D-"+stable_hash({"origin":name,"kind":kind})[:16]
        proposals.append(entry)
    integrity=mesh.get("integrity","HOLD")
    return {"schema":"formic-diaspora-exchange-v1","observed_at":at,
            "mesh_integrity":integrity,"idea_count":len(proposals),
            "proposals":proposals,"autonomous_writes":False,
            "note":"Ideas exchanged as public evidence reports, never as votes or automatically executed repository changes."}

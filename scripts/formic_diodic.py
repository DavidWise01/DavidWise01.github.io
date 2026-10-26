"""FORMIC diodic cycle: FORMIC ingress -> observation -> HEGEMON -> FORMIC egress.
Read-only provenance chain, deterministic JSON digest, no automatic enforcement.
"""
import hashlib
import json

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",",":"), ensure_ascii=False)

def close_cycle(report, prior):
    stamp=report["generated_at"]
    incoming={"gate":"FORMIC_IN","at":stamp,"prior_digest":prior.get("diodic",{}).get("digest"),
              "input":"bounded public GitHub metadata"}
    witnesses=[
        {"id":"A","role":"inventory","finding":"complete" if report["complete"] else "incomplete"},
        {"id":"B","role":"continuity","finding":"review flags: "+str(report["review"])},
        {"id":"C","role":"provenance","finding":"public GitHub API; not an intrusion attestation"}
    ]
    damping=report.get("feedback",{})
    decision="HOLD" if damping.get("state") != "OBSERVE" else "YES_OBSERVE"
    output={"gate":"FORMIC_OUT","at":stamp,"decision":decision,
            "execute":False,"outcome":"observation recorded; no firewall or repository mutation"}
    frame={"schema":"formic-diodic-v1","ingress":incoming,
           "witnesses":witnesses,"hegemons_decision":decision,"feedback":damping,"egress":output,
           "boundary":"Every cycle begins and ends with FORMIC; evidence is not authority to execute"}
    frame["digest"]=hashlib.sha256(canonical(frame).encode("utf-8")).hexdigest()
    return frame

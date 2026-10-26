"""FORMIC v1.0 observational phase-lag estimator. Zero interventions."""
from datetime import datetime

def _time(s):
    try: return datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()
    except (ValueError,AttributeError): return None

def phase(samples, max_lag=6):
    # Rising REVIEW counts define observed pulses, not attacks.
    if len(samples)<4:
        return {"state":"INSUFFICIENT_DATA","pairs":[],"samples":len(samples),"minimum_samples":4}
    names=sorted(set().union(*(set(s.get("counts",{})) for s in samples)))
    pulses={k:[] for k in names}
    for i in range(1,len(samples)):
        a,b=samples[i-1],samples[i]
        timestamp=_time(b.get("at"))
        if timestamp is None: continue
        for k in names:
            if b.get("counts",{}).get(k,0)>a.get("counts",{}).get(k,0):
                pulses[k].append((i,timestamp))
    pairs=[]
    for ia,a in enumerate(names):
        for b in names[ia+1:]:
            candidates=[]
            for i,ta in pulses[a]:
                for j,tb in pulses[b]:
                    lag=j-i
                    if 0<abs(lag)<=max_lag:
                        candidates.append((abs(lag),a if lag>0 else b,b if lag>0 else a,abs(tb-ta)))
            if not candidates: continue
            candidates.sort()
            _,leader,follower,seconds=candidates[0]
            pairs.append({"first":leader,"then":follower,"lag_windows":candidates[0][0],
                          "lag_hours_approx":round(seconds/3600,2),
                          "evidence":"review-count rising edges in bounded observation history",
                          "confidence":"LOW","causality":"NOT_ESTABLISHED",
                          "candidate_pairs":len(candidates)})
    return {"state":"OBSERVATIONAL","pairs":pairs[:25],"samples":len(samples),
            "max_lag_windows":max_lag,
            "limits":"Single nearest pair can be coincidental. Hourly Actions cadence is not exact. No verified infrastructure dependency.",
            "action":"HOLD_NO_EXECUTION"}

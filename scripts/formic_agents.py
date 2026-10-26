"""One deterministic, read-only FORMIC observer agent per public repo cabinet."""
import hashlib

def bind_agents(cabinets, previous, at):
    old = {a.get("cabinet"): a for a in previous.get("agents", [])}
    agents = []
    for cabinet in cabinets:
        name = cabinet["name"]
        stable_id = "F-" + hashlib.sha256(("DavidWise01/" + name).encode()).hexdigest()[:16]
        old_agent = old.get(name, {})
        state = cabinet["state"]
        evidence = {
            "repository": cabinet["url"],
            "branch": cabinet.get("default_branch"),
            "archived": cabinet.get("archived"),
            "visibility": cabinet.get("visibility"),
            "pushed_at": cabinet.get("pushed_at")
        }
        agents.append({
            "id": stable_id,
            "cabinet": name,
            "circuit": cabinet.get("circuit", "UNMAPPED"),
            "mode": "PASSIVE_WITNESS",
            "state": state,
            "observed_at": at,
            "observation_count": min(int(old_agent.get("observation_count", 0)) + 1, 999999),
            "decision": "HOLD" if state == "REVIEW" else "YES_OBSERVE",
            "witnesses": [
                {"id": "A", "what": "Public repository inventoried", "source": cabinet["url"]},
                {"id": "B", "how": "Current lifecycle from public metadata", "detail": state},
                {"id": "C", "why": "Review classification is heuristic; no compromise established", "reasons": cabinet.get("reasons", [])}
            ],
            "evidence": evidence,
            "execute": False
        })
        cabinet["agent_id"] = stable_id
    return agents

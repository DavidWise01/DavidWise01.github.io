"""Reversible advisory feedback: hysteresis and bounded cooldown, no actuation."""
def feedback(report, previous):
    before=previous.get("feedback",{})
    last=before.get("state","OBSERVE")
    review=report["review"]
    streak=before.get("review_streak",0)+1 if review else 0
    clear=before.get("clear_streak",0)+1 if not review else 0
    if review and streak>=3: state="SUSTAINED_REVIEW"
    elif review: state="HOLD_WATCH"
    elif last in ("SUSTAINED_REVIEW","HOLD_WATCH","RECOVERY_WATCH") and clear<2:
        state="RECOVERY_WATCH"
    else: state="OBSERVE"
    emit=(state!=last)
    return {"schema":"formic-feedback-v1","state":state,"previous_state":last,
            "review_streak":min(streak,999),"clear_streak":min(clear,999),
            "state_changed":emit,"advisory":"Investigate persisted change" if state=="SUSTAINED_REVIEW" else "Continue passive observations",
            "hysteresis":{"review_enter":3,"recovery_clear":2},
            "no_execution":True,
            "boundary":"Only complete public inventories update feedback; no repository changes or firewall actuation."}

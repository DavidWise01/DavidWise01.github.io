#!/usr/bin/env python3
"""Offline validation of a Diaspora proposal packet. No GitHub writes."""
import hashlib
import json
import re
import sys
from pathlib import Path

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def check(packet):
    errors=[]
    declared=packet.get("packet_sha256")
    body={k:v for k,v in packet.items() if k!="packet_sha256"}
    if not isinstance(declared,str) or declared!=digest(body):
        errors.append("checksum_mismatch")
    repo=body.get("target_repository","")
    if not re.fullmatch(r"DavidWise01/[A-Za-z0-9_.-]+",repo):
        errors.append("out_of_scope_repository")
    if body.get("status")!="DRAFT_ONLY" or body.get("diff")!="NOT_GENERATED":
        errors.append("not_a_draft_packet")
    if body.get("approval")!="REQUIRED":
        errors.append("approval_boundary_missing")
    if not body.get("evidence") or not isinstance(body.get("checks"),list) or len(body["checks"])<2:
        errors.append("missing_evidence_or_checks")
    if not str(body.get("proposed_branch","")).startswith("diaspora/"):
        errors.append("invalid_change_branch")
    return errors

def main(argv):
    if len(argv)!=2:
        print("Usage: python scripts/formic_verify_packet.py packet.json")
        return 2
    packet=json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    errors=check(packet)
    print(json.dumps({"status":"PASS" if not errors else "HOLD","errors":errors},sort_keys=True))
    return 0 if not errors else 1

if __name__=="__main__":
    raise SystemExit(main(sys.argv))

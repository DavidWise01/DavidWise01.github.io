"""FORMIC frozen-baseline smoke tests; synthetic data, no network."""
import unittest
from formic_feedback import feedback
from formic_diodic import close_cycle
from formic_heartbeat import heartbeat
from formic_grid import build_grid
from formic_rhythm import rhythm
from formic_phase import phase
from formic_agents import bind_agents
from formic_diaspora import build_diaspora
from formic_exchange import exchange

class FormicFreezeTest(unittest.TestCase):
    def test_feedback_hysteresis(self):
        prev={}
        for state in ("HOLD_WATCH","HOLD_WATCH","SUSTAINED_REVIEW"):
            result=feedback({"review":1},prev)
            self.assertEqual(result["state"],state)
            self.assertTrue(result["no_execution"])
            prev={"feedback":result}
        self.assertEqual(feedback({"review":0},prev)["state"],"RECOVERY_WATCH")
        prev={"feedback":feedback({"review":0},prev)}
        self.assertEqual(feedback({"review":0},prev)["state"],"OBSERVE")

    def test_diodic_closure(self):
        rep={"generated_at":"2026-10-26T00:00:00+00:00","complete":True,"review":0,
             "feedback":{"state":"OBSERVE"}}
        frame=close_cycle(rep,{})
        self.assertEqual(frame["ingress"]["gate"],"FORMIC_IN")
        self.assertEqual(frame["egress"]["gate"],"FORMIC_OUT")
        self.assertFalse(frame["egress"]["execute"])
        self.assertEqual(len(frame["digest"]),64)
        self.assertEqual(close_cycle(rep,{})["digest"],frame["digest"])

    def test_one_agent_per_cabinet(self):
        cabinets=[{"name":"ud0","url":"https://github.com/DavidWise01/ud0","state":"ACTIVE","circuit":"CORE"},
                  {"name":"az1","url":"https://github.com/DavidWise01/az1","state":"REVIEW","circuit":"CORE"}]
        agents=bind_agents(cabinets,{}, "2026-10-26T00:00:00Z")
        self.assertEqual(len(agents),len(cabinets))
        self.assertEqual(len({a["id"] for a in agents}),len(cabinets))
        self.assertTrue(all(a["execute"] is False for a in agents))
        self.assertTrue(all(len(a["witnesses"])==3 for a in agents))
        self.assertEqual(agents[0]["id"],bind_agents(cabinets,{}, "2026-10-27T00:00:00Z")[0]["id"])

    def test_diaspora_1_to_1(self):
        c=[{"name":"ud0","url":"https://github.com/DavidWise01/ud0","state":"ACTIVE","circuit":"CORE"}]
        a=bind_agents(c,{},"2026-10-26T00:00:00Z")
        result=build_diaspora(c,a,"2026-10-26T00:00:00Z")
        self.assertEqual(result["integrity"],"PASS")
        self.assertEqual(len(result["links"]),1)
        self.assertFalse(result["execute"])
        broken=build_diaspora(c,[],"2026-10-26T00:00:00Z")
        self.assertEqual(broken["integrity"],"HOLD")
        self.assertIn("agent_cardinality_mismatch",broken["faults"][0]["errors"])

    def test_diaspora_idea_exchange(self):
        cabinets=[{"name":"ud0","url":"https://github.com/DavidWise01/ud0",
                   "state":"ACTIVE","pages_url":"https://davidwise01.github.io/ud0/"},
                  {"name":"az1","url":"https://github.com/DavidWise01/az1",
                   "state":"REVIEW","pages_url":None}]
        agents=bind_agents(cabinets,{},"2026-10-26T00:00:00Z")
        mesh=build_diaspora(cabinets,agents,"2026-10-26T00:00:00Z")
        ideas=exchange(cabinets,agents,mesh,"2026-10-26T00:00:00Z")
        self.assertEqual(ideas["idea_count"],2)
        self.assertFalse(ideas["autonomous_writes"])
        self.assertTrue(all(p["proposal_state"]=="HOLD_UNVERIFIED" for p in ideas["proposals"]))
        self.assertTrue(all(p["bounds"]["requires_owner_approval"] for p in ideas["proposals"]))
        self.assertTrue(all(p["verification"]["applied"] is False for p in ideas["proposals"]))
        self.assertTrue(all(not p["implementation"]["write"] for p in ideas["proposals"]))
        self.assertEqual(len({p["id"] for p in ideas["proposals"]}),2)
        self.assertTrue(all(len(p["packet_sha256"])==64 for p in ideas["proposals"]))
        self.assertTrue(all(p["change_packet"]["diff"]=="NOT_GENERATED" for p in ideas["proposals"]))
        self.assertTrue(all(p["change_packet"]["approval"]=="REQUIRED" for p in ideas["proposals"]))

    def test_observational_engines(self):
        items=[{"name":"ud0","state":"ACTIVE","archived":False,"fork":False},
               {"name":"az1","state":"REVIEW","archived":False,"fork":False},
               {"name":"older","state":"REST","archived":True,"fork":False}]
        grid=build_grid(items)
        self.assertEqual(grid["cabinet_count"],3)
        beat=heartbeat(items,{},"2026-10-26T00:00:00+00:00")
        self.assertEqual(beat["signal"],"TRANSIENT_REVIEW")
        r=rhythm(items,{},"2026-10-26T00:00:00+00:00")
        self.assertEqual(r["current"]["CORE"],1)
        self.assertEqual(phase(r["samples"])["state"],"INSUFFICIENT_DATA")
        self.assertFalse(grid["circuits"][0]["shared_failure_confirmed"])

if __name__=="__main__":
    unittest.main()

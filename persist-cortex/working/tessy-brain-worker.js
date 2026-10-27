/* PERSIST CORTEX — Tessy {{i}} Somorphic Brain Globule
 * Adapted from OASIS MNP-3D Build 028/032:
 * https://github.com/DavidWise01/oasis/blob/main/docs/mnp-3d/index.html
 * Canonical deduction rules C1..C6, guarded DERIVED/CONFLICT/ABSTAIN.
 * Read-only, bounded, structured-triple inference; no DOM/network/storage.
 */
'use strict';
const WORKER_VERSION='tessy-i-somorphic-v1';
const RULES=[
{id:'C1',left:['X','pursues','Y'],right:['Y','requires','Z'],out:['X','initiates','Z']},
{id:'C2',left:['X','initiates','Y'],right:['Y','causes','Z'],out:['X','faces','Z']},
{id:'C3',left:['X','uses','Y'],right:['Y','reveals','Z'],out:['X','observes','Z']},
{id:'C4',left:['X','observes','Y'],right:['Y','provides','Z'],out:['X','obtains','Z']},
{id:'C5',left:['X','plants','Y'],right:['Y','weakens','Z'],out:['X','undermines','Z']},
{id:'C6',left:['X','undermines','Y'],right:['Y','supports','Z'],out:['X','threatens','Z']}
];
const LIMITS={premises:48,passes:8,facts:320,stepProof:64,text:160};
const validTriple=t=>Array.isArray(t)&&t.length===3&&t.every(v=>typeof v==='string'&&v.length>0&&v.length<=LIMITS.text);
const key=t=>JSON.stringify(t);
function unify(pattern,triple,b){const next={...b};for(let i=0;i<3;i++){const p=pattern[i],v=triple[i];if(/^[XYZ]$/.test(p)){if(next[p]!==undefined&&next[p]!==v)return null;next[p]=v}else if(p!==v)return null}return next}
const inst=(pattern,b)=>pattern.map(x=>/^[XYZ]$/.test(x)?b[x]:x);
function deduction(premises,goal){
 const facts=new Map(premises.map((p,i)=>[key(p.triple),{triple:p.triple,steps:[],sources:[p.semanticHash]}]));
 let truncated=false;
 for(let pass=0;pass<LIMITS.passes;pass++){
  let changed=false,now=[...facts.values()];
  outer:for(const rule of RULES)for(const x of now){const b1=unify(rule.left,x.triple,{});if(!b1)continue;for(const y of now){const b2=unify(rule.right,y.triple,b1);if(!b2)continue;const out=inst(rule.out,b2),k=key(out);if(facts.has(k))continue;
   const steps=[...x.steps,...y.steps,{rule:rule.id,from:[x.triple,y.triple],to:out}].slice(-LIMITS.stepProof);
   const sources=[...new Set([...x.sources,...y.sources])];
   facts.set(k,{triple:out,steps,sources});changed=true;
   if(facts.size>=LIMITS.facts){truncated=true;break outer}
  }}
  if(!changed||truncated)break;
 }
 const got=facts.get(key(goal));return{decision:got?'DERIVED':'ABSTAIN',steps:got?.steps||[],sources:got?.sources||[],derivedFacts:facts.size,truncated};
}
function evaluate(req){
 if(!req||!Array.isArray(req.premises)||req.premises.length>LIMITS.premises||!validTriple(req.goal))throw Error('Invalid or oversized inference input');
 if(!Number.isInteger(req.y)||req.y<0||req.y>7||!Number.isInteger(req.x)||req.x<0||req.x>23)throw Error('Invalid {{i}}/{{d}} address');
 if(req.premises.some(p=>!p||!validTriple(p.triple)||typeof p.semanticHash!=='string'||!/^[a-f0-9]{64}$/.test(p.semanticHash)))throw Error('Premise must carry a valid SHA-256 semantic source');
 const positive=deduction(req.premises,req.goal),negativeGoal=[req.goal[0],'not-'+req.goal[1],req.goal[2]],negative=deduction(req.premises,negativeGoal);
 // Fail closed if closure is incomplete and goal cannot be justified.
 let decision='ABSTAIN';if(positive.truncated||negative.truncated)decision='ABSTAIN';else if(positive.decision==='DERIVED'&&negative.decision==='DERIVED')decision='CONFLICT';else if(positive.decision==='DERIVED')decision='DERIVED';
 const opposition=negative.decision==='DERIVED'?{goal:negativeGoal,sourceHashes:negative.sources}:null;
 return{engine:WORKER_VERSION,route:{i:'V'+req.y,d:'ABCDEFGHIJKLMNOPQRSTUVWX'[req.x],degrees:req.x*15},decision,goal:req.goal,proof:decision==='DERIVED'||decision==='CONFLICT'?positive.steps:[],sourceHashes:positive.sources,opposition,sourceCount:req.premises.length,derivedFacts:positive.derivedFacts,exhaustive:!positive.truncated&&!negative.truncated,write:'NONE',status:'READ_ONLY'};
}
self.onmessage=ev=>{const {id,request}=ev.data||{};try{self.postMessage({id,ok:true,receipt:evaluate(request)})}catch(e){self.postMessage({id,ok:false,error:String(e.message||e)})}};

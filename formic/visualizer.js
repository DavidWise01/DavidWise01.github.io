// FORMIC 3D cabinet arcade v2.2 — public metadata, one display agent per repository.
const THREE_URL='https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js';
export async function mountFormic3D(host,{dataUrl='./arcade.json'}={}){
 const label=document.createElement('div');label.style.cssText='position:absolute;left:12px;top:10px;z-index:2;background:#07131ddd;color:#d5fcf4;padding:7px 11px;border:1px solid #3c7980;border-radius:8px;font:12px system-ui;pointer-events:none;max-width:95%';label.textContent='FORMIC · loading repository cabinets';host.append(label);
 let T;try{T=await import(THREE_URL)}catch(e){label.textContent='Three.js unavailable. 2D cabinet list remains accessible.';return}
 const scene=new T.Scene();scene.background=new T.Color(0x07101d);
 const camera=new T.PerspectiveCamera(48,1,.1,450);camera.position.set(0,12,185);camera.lookAt(0,0,0);
 let renderer;try{renderer=new T.WebGLRenderer({antialias:true,powerPreference:'low-power'})}catch(e){label.textContent='WebGL unavailable. 2D cabinet list remains accessible.';return}
 renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));host.prepend(renderer.domElement);
 scene.add(new T.HemisphereLight(0xc6f5ff,0x18334c,2));
 const light=new T.DirectionalLight(0xffffff,2.2);light.position.set(-12,28,24);scene.add(light);
 const floor=new T.GridHelper(145,18,0x2b6375,0x153447);floor.position.y=-66;scene.add(floor);
 const core=new T.Mesh(new T.IcosahedronGeometry(3.5,1),new T.MeshStandardMaterial({color:0x3cf0c6,emissive:0x126b6b,wireframe:true}));
 core.position.set(0,-15,-18);scene.add(core);
 const ring=new T.Mesh(new T.TorusGeometry(5,.11,8,72),new T.MeshBasicMaterial({color:0xa48fff}));ring.position.copy(core.position);scene.add(ring);
 const shells=[],materials=[],textures=[],wiring=[];const ray=new T.Raycaster(),mouse=new T.Vector2();
 const focus=new T.Vector3(0,-36,0);
 const shellGeo=new T.BoxGeometry(3.3,5.3,2.35),frontGeo=new T.PlaneGeometry(2.9,3.55);
 const stateColors={ACTIVE:'#37ebc3',REST:'#93a5bc',REVIEW:'#ffc76a',RECOVERY:'#b99dff'};
 const escapeName=s=>String(s||'repository').slice(0,32);
 function thumbnail(row){
  // Procedural per-repository art: clearly identifies a repo, not a screenshot.
  const c=document.createElement('canvas');c.width=192;c.height=232;
  const x=c.getContext('2d');x.scale(.5,.5);
  const name=escapeName(row.name),state=row.state||'ACTIVE',accent=stateColors[state]||'#37ebc3';
  const hue=Array.from(name).reduce((a,ch)=>a+ch.charCodeAt(0),0)%360;
  const grad=x.createLinearGradient(0,0,384,464);grad.addColorStop(0,'hsl('+hue+',43%,19%)');grad.addColorStop(1,'#060b18');x.fillStyle=grad;x.fillRect(0,0,384,464);
  x.strokeStyle=accent;x.lineWidth=7;x.strokeRect(12,12,360,440);
  x.fillStyle=accent;x.font='bold 16px monospace';x.fillText('GITHUB · '+state,27,42);
  // An individual geometric glyph derived from the repository name.
  x.save();x.translate(192,182);x.rotate(hue*Math.PI/180);x.strokeStyle=accent;x.lineWidth=5;
  for(let i=0;i<5;i++){x.rotate(Math.PI/5);x.strokeRect(-54,-54,108,108)}x.restore();
  x.fillStyle='#e5fbff';x.font='bold 28px system-ui';
  const words=name.match(/.{1,18}/g)||[name];words.slice(0,2).forEach((v,i)=>x.fillText(v,26,333+i*34));
  x.font='15px monospace';x.fillStyle='#a8d7e4';x.fillText(row.agent_id?'AGENT '+row.agent_id.slice(0,15):'AGENT · UNBOUND',26,414);
  const texture=new T.CanvasTexture(c);texture.colorSpace=T.SRGBColorSpace;textures.push(texture);return texture;
 }
 let rows=[],agents=new Map();
 function clear(){for(const o of shells)scene.remove(o);shells.length=0;for(const o of wiring){scene.remove(o);o.geometry.dispose();o.material.dispose()}wiring.length=0;for(const m of materials)m.dispose();materials.length=0;for(const t of textures)t.dispose();textures.length=0}
 // FORMIC SILO: 4 cabinet sites, 1 coupler, repeated four times.
 // Each module houses 16 cabinets; additional modules are adjacent silos.
 function addWire(points,color,opacity=.32){
  const geo=new T.BufferGeometry().setFromPoints(points.map(p=>new T.Vector3(p.x,p.y,p.z)));
  const mat=new T.LineBasicMaterial({color,transparent:true,opacity,depthWrite:false});
  const line=new T.Line(geo,mat);scene.add(line);wiring.push(line);
 }
 function fill(input,source){
  clear();
  const coreSet=new Set(['ud0','az1','oasis','davidwise01.github.io','the.source','root0']);
  const ordered=[...input].sort((a,b)=>{
   const ac=coreSet.has(String(a.name).toLowerCase())?0:1,bc=coreSet.has(String(b.name).toLowerCase())?0:1;
   return ac-bc||String(a.name).localeCompare(String(b.name));
  });
  // Every row gets exactly one unique shelf slot. 4×1×4×1×4×1×4.
  // 16 cabinets + 3 coupling levels per silo; never treat a coupler as a repo.
  const MAX=640,PER_SILO=16;
  rows=ordered.slice(0,MAX);
  const siloCount=Math.ceil(rows.length/PER_SILO);
  const columns=Math.max(1,Math.ceil(Math.sqrt(siloCount)));
  const siloWidth=19,spacing=4.4,shelfHeight=7.6,ground=-49;
  for(let silo=0;silo<siloCount;silo++){
   const col=silo%columns,line=Math.floor(silo/columns);
   const baseX=(col-(columns-1)/2)*siloWidth;
   const baseZ=-line*17;
   const trunkX=baseX, trunkZ=baseZ-4;
   // Individual vertical service riser with 3 single-coupler junctions.
   addWire([{x:trunkX,y:ground-2,z:trunkZ},{x:trunkX,y:ground+4*shelfHeight+4,z:trunkZ}],0x4dc9bc,.55);
   for(let tier=0;tier<4;tier++){
    const y=ground+tier*shelfHeight;
    for(let pos=0;pos<4;pos++){
     const index=silo*PER_SILO+tier*4+pos;if(index>=rows.length)continue;
     const row=rows[index],x=baseX+(pos-1.5)*spacing,z=baseZ;
     const color=new T.Color(stateColors[row.state]||'#37ebc3');
     const mat=new T.MeshStandardMaterial({color:0x152d3b,metalness:.4,roughness:.4,emissive:color,emissiveIntensity:.16});
     materials.push(mat);
     const mesh=new T.Mesh(shellGeo,mat);mesh.position.set(x,y,z);mesh.userData=row;scene.add(mesh);shells.push(mesh);
     const screenMat=new T.MeshBasicMaterial({map:thumbnail(row),side:T.DoubleSide});materials.push(screenMat);
     const face=new T.Mesh(frontGeo,screenMat);face.position.set(x,y+.25,z+1.2);face.userData=row;scene.add(face);shells.push(face);
     // Cabinet agent port -> tier riser -> FORMIC central uplink.
     addWire([{x,y,z:-0+baseZ-1.5},{x,y,z:trunkZ},{x:trunkX,y,z:trunkZ}],color,.28);
    }
    if(tier<3){
     const junction={x:trunkX,y:y+shelfHeight/2,z:trunkZ};
     const nodeMat=new T.MeshBasicMaterial({color:0xc19dff});materials.push(nodeMat);
     const node=new T.Mesh(new T.OctahedronGeometry(.65),nodeMat);
     node.position.set(junction.x,junction.y,junction.z);scene.add(node);shells.push(node);
     addWire([junction,{x:trunkX,y:junction.y,z:trunkZ-2}],0xb99dff,.6);
    }
   }
   addWire([{x:trunkX,y:ground+4*shelfHeight+4,z:trunkZ},{x:0,y:0,z:-18}],0x69d6cc,.20);
  }
  // Bring the first silo into the frame rather than showing an empty upper void.
  const centerX=0,centerY=ground+1.5*shelfHeight;
  focus.set(centerX,centerY,0);
  label.textContent=rows.length+' repository cabinets · '+siloCount+' silo(s) · '+source+' · 4×1×4×1×4×1×4';
 }
 async function load(){
  try{
   const response=await fetch(dataUrl+'?t='+Date.now(),{cache:'no-store'});
   if(!response.ok)throw Error('snapshot HTTP '+response.status);
   const data=await response.json();
   if(!data.complete||!Array.isArray(data.cabinets)||!data.cabinets.length)throw Error('missing inventory');
   agents=new Map((data.agents||[]).map(a=>[a.cabinet,a]));
   fill(data.cabinets.map(c=>({...c,agent_id:c.agent_id||agents.get(c.name)?.id})), 'persistent inventory');return;
  }catch(e){}
  try{
   const response=await fetch('https://api.github.com/users/DavidWise01/repos?type=public&sort=full_name&per_page=100',{headers:{Accept:'application/vnd.github+json'}});
   if(!response.ok)throw Error('GitHub HTTP '+response.status);
   const repos=await response.json();if(!Array.isArray(repos)||!repos.length)throw Error('empty');
   fill(repos.map(r=>({name:r.name,url:r.html_url,state:r.archived?'REST':'ACTIVE',agent_id:null})), 'live public GitHub sample (up to 100)');
  }catch(e){label.textContent='Repository inventory unavailable; no synthetic cabinets presented.'}
 }
 renderer.domElement.addEventListener('click',event=>{
  const box=renderer.domElement.getBoundingClientRect();
  mouse.set(((event.clientX-box.left)/box.width)*2-1,-((event.clientY-box.top)/box.height)*2+1);
  ray.setFromCamera(mouse,camera);const hit=ray.intersectObjects(shells)[0];if(!hit)return;
  const r=hit.object.userData;const agent=agents.get(r.name)||null;
  label.textContent=r.name+' · '+r.state+(agent?' · '+agent.id:' · agent not yet published');
  host.dispatchEvent(new CustomEvent('formic-cabinet-selected',{detail:{cabinet:r.name,agent,url:r.url||null}}));
 });
 let yaw=0,zoom=94,drag=false,startX=0,downX=0;
 renderer.domElement.addEventListener('pointerdown',e=>{drag=true;startX=downX=e.clientX;renderer.domElement.setPointerCapture(e.pointerId)});
 renderer.domElement.addEventListener('pointerup',()=>{drag=false});
 renderer.domElement.addEventListener('pointermove',e=>{if(drag){yaw=Math.max(-.7,Math.min(.7,yaw+(e.clientX-startX)*.003));startX=e.clientX}});
 renderer.domElement.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(35,Math.min(240,zoom+Math.sign(e.deltaY)*4))},{passive:false});
 const resize=()=>{const w=Math.max(320,host.clientWidth),h=Math.max(280,host.clientHeight);renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix()};
 const observer=new ResizeObserver(resize);observer.observe(host);resize();
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');let alive=true;
 function animate(t){if(!alive)return;requestAnimationFrame(animate);const tick=t*.001;
  if(!reduced.matches){core.rotation.y=tick*.18;ring.rotation.z=tick*.1}
  camera.position.set(focus.x+Math.sin(yaw)*zoom,focus.y+Math.max(9,zoom*.16),focus.z+Math.cos(yaw)*zoom);
  camera.lookAt(focus);renderer.render(scene,camera)}
 await load();requestAnimationFrame(animate);
 return {refresh:load,destroy(){alive=false;observer.disconnect();clear();shellGeo.dispose();frontGeo.dispose();renderer.dispose();renderer.domElement.remove()}};
}

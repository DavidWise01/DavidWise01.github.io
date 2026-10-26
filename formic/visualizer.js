// FORMIC Three.js visualization v2.0. Read-only: no GitHub mutations or network scanning.
const THREE_URL='https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js';
export async function mountFormic3D(host,{mode='arcade',dataUrl='./arcade.json'}={}){
  const status=document.createElement('div');status.className='formic3d-status';status.textContent='Loading Three.js display…';host.append(status);
  let THREE;
  try{THREE=await import(THREE_URL)}catch(e){status.textContent='Three.js unavailable; 2D monitoring remains active.';return}
  if(!host.isConnected)return;
  const scene=new THREE.Scene();scene.background=new THREE.Color(0x070e1b);scene.fog=new THREE.FogExp2(0x070e1b,.014);
  const rect=()=>({w:Math.max(320,host.clientWidth),h:Math.max(260,host.clientHeight)});
  let {w,h}=rect(),renderer;
  try{renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'low-power'})}catch(e){status.textContent='WebGL unavailable; monitoring remains active.';return}
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.setSize(w,h);host.prepend(renderer.domElement);
  const camera=new THREE.PerspectiveCamera(52,w/h,.1,600);camera.position.set(0,30,74);
  const ambient=new THREE.AmbientLight(0xb5e3ff,1.0);scene.add(ambient);
  const point=new THREE.PointLight(0x52efc9,100,100);point.position.set(0,15,10);scene.add(point);
  const grid=new THREE.GridHelper(120,30,0x295c72,0x152e44);grid.position.y=-12;scene.add(grid);
  const coreGroup=new THREE.Group();scene.add(coreGroup);
  const core=new THREE.Mesh(new THREE.IcosahedronGeometry(8,2),new THREE.MeshStandardMaterial({color:0x43dcbf,emissive:0x167a79,emissiveIntensity:.6,wireframe:true}));
  coreGroup.add(core);
  const ring=new THREE.Mesh(new THREE.TorusGeometry(14,.27,10,90),new THREE.MeshStandardMaterial({color:0x8a8aff,emissive:0x3b2a99,emissiveIntensity:.7}));
  ring.rotation.x=1;coreGroup.add(ring);
  const supports=[];let cabinets=[];let agentsByCabinet=new Map();
  const raycaster=new THREE.Raycaster(),pointer=new THREE.Vector2();
  const boxGeo=new THREE.BoxGeometry(1.9,2.9,1.4),colors={ACTIVE:0x4ce4bc,REST:0x607f98,REVIEW:0xffba6b,RECOVERY:0xb39bff};
  function populate(rows){
    supports.forEach(o=>{scene.remove(o);o.material.dispose()});supports.length=0;
    cabinets=rows.slice(0,1200);
    const n=cabinets.length;
    cabinets.forEach((r,i)=>{
      // A bounded multi-ring arcade: no reliance on speculative physical topology.
      const ringN=Math.floor(i/90),slot=i%90,angle=2*Math.PI*slot/90+ringN*.1;
      const radius=21+ringN*5.3,y=((i%9)-4)*.3-6+Math.floor(i/360)*3;
      const mat=new THREE.MeshStandardMaterial({color:colors[r.state]||0x4ce4bc,emissive:colors[r.state]||0x4ce4bc,emissiveIntensity:.18,metalness:.3,roughness:.4});
      const mesh=new THREE.Mesh(boxGeo,mat);mesh.position.set(Math.cos(angle)*radius,y,Math.sin(angle)*radius);
      mesh.rotation.y=-angle;mesh.userData={name:r.name,state:r.state,url:r.url,agent:agentsByCabinet.get(r.name)};scene.add(mesh);supports.push(mesh);
      const dot=new THREE.Mesh(new THREE.SphereGeometry(.48,7,6),new THREE.MeshBasicMaterial({color:0xe6f7ff}));dot.position.set(mesh.position.x,mesh.position.y+2.2,mesh.position.z);dot.userData=mesh.userData;scene.add(dot);supports.push(dot);
    });
    status.textContent=(n?n+' visible repository cabinets':'27 FORMIC sentinels')+' · Three.js · visualization only';
  }
  async function load(){try{
    const r=await fetch(dataUrl+(dataUrl.includes('?')?'&':'?')+'t='+Date.now(),{cache:'no-store'});
    if(!r.ok)throw Error('HTTP '+r.status);
    const obj=await r.json();if(!obj.complete||!Array.isArray(obj.cabinets))throw Error('incomplete');
    agentsByCabinet=new Map((obj.agents||[]).map(a=>[a.cabinet,a]));populate(obj.cabinets);
  }catch(e){status.textContent='Live cabinet inventory unavailable — showing simulated hive.';
    const fallback=Array.from({length:27},(_,i)=>({name:'FORMIC '+(i+1),state:'ACTIVE'}));populate(fallback);
    status.textContent='27 simulated sentinels · no published arcade inventory';}}
  let dragging=false,lastX=0,rotation=0,zoom=74;
  renderer.domElement.addEventListener('click',e=>{const bounds=renderer.domElement.getBoundingClientRect();pointer.set(((e.clientX-bounds.left)/bounds.width)*2-1,-((e.clientY-bounds.top)/bounds.height)*2+1);raycaster.setFromCamera(pointer,camera);const hits=raycaster.intersectObjects(supports,false);if(!hits.length)return;const info=hits[0].object.userData;const agent=info.agent;status.textContent=agent?info.name+' · agent '+agent.id+' · '+agent.state+' · '+agent.decision+' · observations '+agent.observation_count:info.name+' · simulated cabinet';host.dispatchEvent(new CustomEvent('formic-cabinet-selected',{detail:{cabinet:info.name,agent:agent||null}}));});
  renderer.domElement.addEventListener('pointerdown',e=>{dragging=true;lastX=e.clientX;renderer.domElement.setPointerCapture(e.pointerId)});
  renderer.domElement.addEventListener('pointerup',()=>dragging=false);
  renderer.domElement.addEventListener('pointermove',e=>{if(dragging){rotation+=(e.clientX-lastX)*.006;lastX=e.clientX}});
  renderer.domElement.addEventListener('wheel',e=>{zoom=Math.max(34,Math.min(135,zoom+Math.sign(e.deltaY)*5));e.preventDefault()},{passive:false});
  let alive=true,raf=0;const clock=new THREE.Clock();
  const observer=new ResizeObserver(()=>{const d=rect();if(d.w!==w||d.h!==h){w=d.w;h=d.h;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix()}});observer.observe(host);
  const media=window.matchMedia('(prefers-reduced-motion: reduce)');
  function frame(){if(!alive)return;raf=requestAnimationFrame(frame);const t=clock.getElapsedTime();core.rotation.y=t*.12;ring.rotation.z=t*.1;
    coreGroup.rotation.y=rotation+(media.matches?0:t*.035);camera.position.z+=(zoom-camera.position.z)*.04;
    renderer.render(scene,camera)}
  await load();frame();
  return {refresh:load,destroy(){alive=false;cancelAnimationFrame(raf);observer.disconnect();supports.forEach(x=>x.material.dispose());boxGeo.dispose();renderer.dispose();renderer.domElement.remove()}};
}

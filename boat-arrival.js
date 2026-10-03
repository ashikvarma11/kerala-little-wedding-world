import * as T from 'three';

// A short arrival on a vallam, followed by a walk from the boat to the bank.
export function createBoatArrival({scene, boat, player, groom, camera, reduced, onFinish}) {
  const dock = new T.Group();
  dock.name = 'ArrivalJetty';
  scene.add(dock);
  const timber = new T.MeshStandardMaterial({color: '#785331', roughness: 1});
  const add = (w,h,d,x,y,z,material=timber) => {
    const mesh = new T.Mesh(new T.BoxGeometry(w,h,d), material);
    mesh.position.set(x,y,z);mesh.castShadow=true;mesh.receiveShadow=true;dock.add(mesh);return mesh;
  };
  for(let i=0;i<13;i++) add(.23,.14,1.05,5.9+i*.2,.51,3);
  for(const x of [6.1,7.25,8.3]) for(const z of [2.58,3.42]) add(.13,1.7,.13,x,-.18,z);
  const gangplank = add(1.1,.07,.64,8.62,.16,3);
  gangplank.rotation.z=-Math.atan2(.84,1.1);
  // Small ripples follow the hull without a particle-system cost on phones.
  const ripples = [];
  for(let i=0;i<3;i++) {
    const material = new T.MeshBasicMaterial({color:'#a5d5ca',transparent:true,opacity:.22,depthWrite:false,side:T.DoubleSide});
    const ripple = new T.Mesh(new T.RingGeometry(.52,.56,32),material);
    ripple.rotation.x=-Math.PI/2;ripple.position.y=-.645;ripple.castShadow=false;
    scene.add(ripple);ripples.push(ripple);
  }
  boat.name = 'ArrivalVallam';
  const seat=new T.Mesh(new T.BoxGeometry(.74,.07,.23),timber);
  seat.name='VallamSeat';seat.scale.setScalar(1/boat.scale.x);seat.position.set(0,.65/boat.scale.y,0);seat.castShadow=true;boat.add(seat);
  const start = new T.Vector3(12.8,-.56,6.8), berth = new T.Vector3(9.15,-.56,3);
  const boatFloor = -.27, shore = new T.Vector3(5.8,.58,3);
  let time=0, active=true;
  const world=document.querySelector('#world'), overlay=document.querySelector('#boat-intro');
  world.classList.add('arriving');overlay.hidden=false;
  const status=document.querySelector('#arrival-status');
  function finish() {
    if(!active)return;
    active=false;boat.position.copy(berth);boat.rotation.set(0,Math.PI,0);
    player.position.copy(shore);player.rotation.y=-Math.PI/2;
    player.scale.setScalar(.8);
    groom.update(0,0,true);
    gangplank.visible=false;ripples.forEach(r=>r.visible=false);
    world.classList.remove('arriving');overlay.hidden=true;
    document.querySelector('#skip-arrival').blur();
    onFinish();
  }
  document.querySelector('#skip-arrival').onclick=finish;
  const smooth = t => {t=T.MathUtils.clamp(t,0,1);return t*t*(3-2*t);};
  function update(dt, elapsed) {
    if(!active) {
      if(!reduced){boat.position.y=berth.y+Math.sin(elapsed*1.3)*.025;boat.rotation.z=Math.sin(elapsed)*.018;}
      return false;
    }
    time+=dt;
    const before=player.position.clone();
    if(time<4.5) {
      const t=smooth(time/3.8);
      boat.position.lerpVectors(start,berth,t);boat.position.y+=Math.sin(time*2)*.025;
      boat.rotation.set(0,T.MathUtils.lerp(-2.38,-Math.PI,t),Math.sin(time*1.6)*.02);
      player.position.set(boat.position.x,boatFloor+(boat.position.y-berth.y),boat.position.z);
      player.rotation.y=boat.rotation.y;
      const seated=1-smooth((time-3.8)/.7);
      player.scale.setScalar(.8+.2*seated);
      groom.update(dt,0,false,{rowing:seated,time:Math.min(time,3.8)});
    } else {
      boat.position.copy(berth);boat.rotation.set(0,Math.PI,0);
      const boarding=T.MathUtils.clamp((time-4.5)/1.15,0,1);
      if(boarding<1) {
        player.position.set(T.MathUtils.lerp(9.15,8.05,boarding),T.MathUtils.lerp(boatFloor,.58,smooth(boarding))+Math.sin(boarding*Math.PI)*.08,3);
      } else {
        player.position.lerpVectors(new T.Vector3(8.05,.58,3),shore,T.MathUtils.clamp((time-5.65)/1.75,0,1));
      }
      player.rotation.y=-Math.PI/2;
      groom.update(dt,Math.hypot(player.position.x-before.x,player.position.z-before.z),false);
      if(status.textContent!=='Welcome ashore')status.textContent='Welcome ashore';
    }
    ripples.forEach((r,i)=>{
      const phase=(time*.7+i/3)%1;r.position.x=boat.position.x;r.position.z=boat.position.z;
      r.scale.setScalar(1+phase*2);r.material.opacity=(1-phase)*.2;
    });
    // Track the arrival closely enough to read on portrait screens.
    const handoff=smooth((time-7.4)/.65);
    const goal=new T.Vector3(player.position.x+T.MathUtils.lerp(3.4,5.2,handoff),player.position.y+T.MathUtils.lerp(3.15,3.6,handoff),player.position.z+4.6*(1-handoff));
    camera.position.lerp(goal,time<=dt?1:1-Math.exp(-dt*5));
    camera.lookAt(player.position.x-T.MathUtils.lerp(.65,1.35,handoff),player.position.y+T.MathUtils.lerp(.7,1.15,handoff),player.position.z);
    if(time>=8.05)finish();
    return active;
  }
  if(reduced)finish();
  return {update,finish,get active(){return active;}};
}

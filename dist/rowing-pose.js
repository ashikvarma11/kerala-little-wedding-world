import * as T from 'three';

export function createRowingPose(root, model, animations) {
  const baseY=model.position.y;
  const paddle=new T.Group();paddle.name='RowingPaddle';root.add(paddle);
  const wood=new T.MeshStandardMaterial({color:'#8e6035',roughness:.85});
  const shaft=new T.Mesh(new T.CylinderGeometry(.016,.019,1.42,8),wood);
  shaft.position.y=-.63;paddle.add(shaft);
  const blade=new T.Mesh(new T.BoxGeometry(.18,.38,.035),wood);
  blade.position.y=-1.36;paddle.add(blade);
  paddle.traverse(o=>{if(o.isMesh)o.castShadow=true;});paddle.visible=false;
  const bones=name=>model.getObjectByName(name);
  const gripping=T.AnimationClip.findByName(animations,'Idle_Sword');
  const gripQuaternions=new Map();
  for(const track of gripping?.tracks || [])if(/(?:Index|Middle|Ring|Pinky|Thumb).*\.quaternion$/.test(track.name)) {
    gripQuaternions.set(track.name.split('.')[0],new T.Quaternion().fromArray(track.createInterpolant().evaluate(0)));
  }
  for(const [name,q] of [...gripQuaternions])if(name.endsWith('R')) {
    gripQuaternions.set(name.slice(0,-1)+'L',new T.Quaternion(q.x,-q.y,-q.z,q.w));
  }
  const rest=[];
  for(const side of ['L','R']) {
    for(const name of ['UpperLeg','LowerLeg','UpperArm','LowerArm','Wrist']) {
      const bone=bones(name+side);rest.push({bone,quaternion:bone.quaternion.clone()});
    }
    const foot=bones('Foot'+side);rest.push({bone:foot,position:foot.position.clone()});
    for(const finger of ['Index','Middle','Ring','Pinky','Thumb'])for(let i=1;i<=3;i++) {
      const bone=bones(finger+i+side);if(bone)rest.push({bone,quaternion:bone.quaternion.clone()});
    }
  }
  const point=bone=>root.worldToLocal(bone.getWorldPosition(new T.Vector3()));
  const toWorld=v=>root.localToWorld(v.clone());
  // Rotate from the existing pose so the bone's authored twist is preserved.
  function aim(bone,child,target,weight) {
    root.updateMatrixWorld(true);
    const origin=bone.getWorldPosition(new T.Vector3());
    const current=child?child.getWorldPosition(new T.Vector3()).sub(origin):new T.Vector3(0,1,0).applyQuaternion(bone.getWorldQuaternion(new T.Quaternion()));
    const desired=toWorld(target).sub(origin).normalize();
    const world=bone.getWorldQuaternion(new T.Quaternion());
    world.premultiply(new T.Quaternion().setFromUnitVectors(current.normalize(),desired));
    const local=bone.parent.getWorldQuaternion(new T.Quaternion()).invert().multiply(world);
    bone.quaternion.slerp(local,weight);root.updateMatrixWorld(true);
  }
  function arm(side,grip,weight) {
    const upper=bones('UpperArm'+side),lower=bones('LowerArm'+side),hand=bones('Wrist'+side);
    const shoulder=point(upper),elbow=point(lower),wrist=point(hand);
    const l1=shoulder.distanceTo(elbow),l2=elbow.distanceTo(wrist);
    const direction=grip.clone().sub(shoulder),distance=T.MathUtils.clamp(direction.length(),Math.abs(l1-l2)+.001,l1+l2-.001);direction.normalize();
    const along=(l1*l1-l2*l2+distance*distance)/(2*distance);
    const bend=new T.Vector3(side==='L'?1:-1,-.7,0);bend.addScaledVector(direction,-bend.dot(direction)).normalize();
    const elbowGoal=shoulder.clone().addScaledVector(direction,along).addScaledVector(bend,Math.sqrt(Math.max(0,l1*l1-along*along)));
    aim(upper,lower,elbowGoal,weight);aim(lower,hand,grip,weight);
    aim(hand,bones('Middle1'+side),grip.clone().add(new T.Vector3(0,0,.08)),weight);
    // Close the fingers around the shaft, retaining the wrist's rig orientation.
    for(const finger of ['Index','Middle','Ring','Pinky','Thumb']) for(let i=1;i<=3;i++) {
      const bone=bones(finger+i+side),grip=gripQuaternions.get(finger+i+side);if(bone&&grip)bone.quaternion.slerp(grip,weight);
    }
  }
  return {
    reset() {rest.forEach(({bone,position,quaternion})=>{if(position)bone.position.copy(position);if(quaternion)bone.quaternion.copy(quaternion);});},
    update(weight,time=0) {
      // Preserve this frame's authored pose before applying temporary overrides.
      rest.forEach(({bone,position,quaternion})=>{if(position)position.copy(bone.position);if(quaternion)quaternion.copy(bone.quaternion);});
      model.position.y=baseY-.4*weight;paddle.visible=weight>.02;
      if(!weight)return;
      root.updateMatrixWorld(true);
      for(const side of ['L','R']) {
        const upper=bones('UpperLeg'+side),lower=bones('LowerLeg'+side),foot=bones('Foot'+side);
        const knee=new T.Vector3(side==='L'?.12:-.12,.43,.38);
        aim(upper,lower,knee,weight);
        const actualKnee=point(lower),footGoal=actualKnee.clone().add(new T.Vector3(0,-.4,.035));
        aim(lower,null,footGoal,weight);
        const local=foot.parent.worldToLocal(toWorld(footGoal));foot.position.lerp(local,weight);
      }
      const phase=time*4.2;
      const upperGrip=new T.Vector3(.02,.85+Math.cos(phase)*.025,.20+Math.sin(phase)*.035);
      const lowerGrip=new T.Vector3(.20,.62+Math.cos(phase)*.025,.26+Math.sin(phase)*.13);
      paddle.position.copy(upperGrip);
      paddle.quaternion.setFromUnitVectors(new T.Vector3(0,-1,0),lowerGrip.clone().sub(upperGrip).normalize());
      arm('R',upperGrip,weight);arm('L',lowerGrip,weight);
    }
  };
}

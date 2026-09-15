import * as T from 'three';

export async function createGroom(loader) {
  const gltf = await loader.loadAsync('assets/wedding-character.glb?v=1');
  const root = new T.Group();
  root.name = 'WeddingCharacter';
  const model = gltf.scene;
  model.updateMatrixWorld(true);
  const bounds = new T.Box3().setFromObject(model);
  const scale = 1.65 / Math.max(.001, bounds.max.y - bounds.min.y);
  model.scale.setScalar(scale);
  model.position.y = -bounds.min.y * scale;
  model.traverse(o => {
    if (o.isMesh) {
      o.castShadow = true;
      o.receiveShadow = true;
      o.frustumCulled = false;
    }
  });
  root.add(model);

  const boneNames = {
    leftArm: 'LeftArm_013', rightArm: 'RightArm_039',
    leftForearm: 'LeftForeArm_014', rightForearm: 'RightForeArm_040',
    leftThigh: 'LeftUpLeg_063', rightThigh: 'RightUpLeg_068',
    leftShin: 'LeftLeg_064', rightShin: 'RightLeg_069',
    spine: 'Spine1_03', hips: 'Hips_01'
  };
  const bones = Object.fromEntries(Object.entries(boneNames).map(([key, name]) => [key, model.getObjectByName(name)]));
  const missing = Object.entries(bones).filter(([, bone]) => !bone).map(([key]) => key);
  if (missing.length) throw new Error(`Wedding character bones missing: ${missing.join(', ')}`);
  const rest = Object.fromEntries(Object.entries(bones).map(([key, bone]) => [key, {
    quaternion: bone.quaternion.clone(), position: bone.position.clone()
  }]));
  const axisX = new T.Vector3(1, 0, 0), axisY = new T.Vector3(0, 1, 0), axisZ = new T.Vector3(0, 0, 1);
  const rotation = new T.Quaternion(), parentWorld = new T.Quaternion(), modelWorld = new T.Quaternion();
  const armDirection = new T.Vector3(), desiredDirection = new T.Vector3();
  model.updateMatrixWorld(true);
  model.getWorldQuaternion(modelWorld);
  const armPose = {};
  for (const [key, forearmKey] of [['leftArm', 'leftForearm'], ['rightArm', 'rightForearm']]) {
    bones[key].parent.getWorldQuaternion(parentWorld);
    const parentRelative = modelWorld.clone().invert().multiply(parentWorld);
    armPose[key] = {
      localDirection: bones[forearmKey].position.clone().normalize(),
      parentInverse: parentRelative.invert()
    };
  }
  let phase = 0, motion = 0;

  function pose(key, angle, axis = axisX) {
    bones[key].quaternion.copy(rest[key].quaternion).multiply(rotation.setFromAxisAngle(axis, angle));
  }

  function poseArm(key, swing) {
    armDirection.copy(armPose[key].localDirection).applyQuaternion(rest[key].quaternion);
    desiredDirection.set(0, -1, swing).normalize().applyQuaternion(armPose[key].parentInverse);
    bones[key].quaternion.copy(rotation.setFromUnitVectors(armDirection, desiredDirection)).multiply(rest[key].quaternion);
  }

  return {
    root,
    update(dt, distance, paused = false) {
      const moving = !paused && distance > .0001;
      motion = paused ? 0 : T.MathUtils.damp(motion, moving ? 1 : 0, 12, dt);
      if (paused) phase = 0;
      if (moving) phase += T.MathUtils.clamp(distance / Math.max(dt, .001), .6, 3.2) * dt * 5.2;
      const stride = Math.sin(phase) * motion;
      const liftL = Math.max(0, -stride) * motion;
      const liftR = Math.max(0, stride) * motion;
      poseArm('leftArm', -.18 * stride);
      poseArm('rightArm', .18 * stride);
      pose('leftForearm', (-.012 - .018 * Math.max(0, stride)) * motion);
      pose('rightForearm', (-.012 - .018 * Math.max(0, -stride)) * motion);
      pose('leftThigh', .24 * stride);
      pose('rightThigh', -.24 * stride);
      pose('leftShin', .20 * liftL);
      pose('rightShin', .20 * liftR);
      pose('spine', .025 * stride, axisY);
      bones.hips.position.copy(rest.hips.position);
      bones.hips.position.y += Math.abs(Math.sin(phase * 2)) * .006 * motion;
      if (motion < .001) {
        motion = 0;
        phase = 0;
      }
    }
  };
}

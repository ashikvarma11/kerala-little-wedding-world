import * as T from 'three';

export async function createGroom(loader) {
  const gltf = await loader.loadAsync('assets/quaternius-modern-man.glb?v=1');
  const root = new T.Group();
  root.name = 'WeddingCharacter';
  const model = gltf.scene;
  const mixer = new T.AnimationMixer(model);
  const clip = name => {
    const animation = T.AnimationClip.findByName(gltf.animations, name);
    if (!animation) throw new Error(`Character animation missing: ${name}`);
    return mixer.clipAction(animation);
  };
  const idle = clip('Idle'), walk = clip('Walk');
  idle.play();
  walk.play().setEffectiveWeight(0);
  mixer.update(0);
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
  let motion = 0;
  return {
    root,
    update(dt, distance, paused = false) {
      const moving = !paused && distance > .0001;
      motion = T.MathUtils.damp(motion, moving ? 1 : 0, 14, dt);
      if (motion < .001) motion = 0;
      idle.setEffectiveWeight(1 - motion);
      walk.setEffectiveWeight(motion);
      // The authored clip stays in place; world.js owns position and heading.
      if (moving) walk.setEffectiveTimeScale(T.MathUtils.clamp(distance / Math.max(dt, .001) / 2.7, .35, 1.3));
      mixer.update(dt);
    }
  };
}

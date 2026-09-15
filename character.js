import * as T from 'three';

// Blender exports its -Y facing character along glTF +Z, matching movement.
export async function createGroom(loader) {
  const gltf = await loader.loadAsync('assets/kerala-groom.glb?v=1');
  const root = new T.Group();
  root.name = 'WeddingGroom';
  const model = gltf.scene;
  const bounds = new T.Box3().setFromObject(model);
  const scale = 1.65 / (bounds.max.y - bounds.min.y);
  model.scale.setScalar(scale);
  model.position.y = -bounds.min.y * scale;
  model.traverse(o => {
    if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; }
  });
  root.add(model);
  const mixer = new T.AnimationMixer(model);
  const clip = name => gltf.animations.find(a => a.name === name);
  if (!clip('Walk') || !clip('Idle')) throw new Error('Groom animation clips missing');
  const walk = mixer.clipAction(clip('Walk')).play();
  const idle = mixer.clipAction(clip('Idle')).play();
  walk.setEffectiveWeight(0);
  let weight = 0;
  return {
    root,
    update(dt, distance, paused = false) {
      const moving = !paused && distance > .0001;
      weight = paused ? 0 : T.MathUtils.damp(weight, moving ? 1 : 0, 18, dt);
      if (weight < .002) weight = 0;
      walk.setEffectiveWeight(weight);
      idle.setEffectiveWeight(1 - weight);
      walk.setEffectiveTimeScale(moving ? T.MathUtils.clamp(distance / dt / 1.6, .65, 1.8) : 1);
      if (!weight) walk.time = 0;
      mixer.update(dt);
    }
  };
}

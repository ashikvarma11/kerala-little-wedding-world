# Current playable character

The live game uses the modern Suit character from Quaternius's **Ultimate Modular Men Pack**, licensed CC0. Source: https://quaternius.com/packs/ultimatemodularcharacters.html. The downloaded CC0 redistribution and modification are documented in `dist/assets/quaternius-modern-man.LICENSE.txt`.

Run `python scripts/prepare_modern_character.py work/quaternius-suit.gltf` to package the downloaded glTF as `dist/assets/quaternius-modern-man.glb`. This removes the pistol mesh and preserves the original skeleton, skin weights and all 24 animation clips. The exported asset is 1,803,136 bytes, with about 6,634 visible triangles and 10 material draws. Its rig includes arms, elbows, wrists, fingers, hips, knees and feet; it does not include a facial animation system.

`dist/character.js` plays the model's original Idle and Walk clips with Three.js AnimationMixer, blending according to actual movement. Movement dialogs transition to idle. The model is normalized to 1.65 world units and faces +Z to match the third-person controller. World movement owns position and heading; the animation does not move the player root.

Validation: browser-rendered front/three-quarter idle and walking previews; movement of both upper arms and upper legs across a walking cycle; no visible pistol; mobile layouts at 390×844 and 320×740; automatic wedding arrival details, close behavior and Directions. Review screenshots and results are under `outputs/modern-character/` (ignored by Git).

## Earlier character experiments

The character is an original stylized Blender model based on the user-supplied portrait. The warm medium skin, pale ivory band-collar kurta, rolled sleeves, gold kasavu mundu, dark swept hair, beard and black bracelet follow that reference. The unseen back and feet are interpreted; simple brown sandals complete the model. The likeness is approximate, not a photogrammetry scan.

`build_groom.py` creates the mesh, 12-bone skeleton, Idle and Walk clips, GLB, editable Blender file and studio review images. Run from the repository root with Blender 4.5:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe' --background --python scripts/build_groom.py
```

The runtime GLB is written to `dist/assets/kerala-groom.glb`; review images and `kerala-groom.blend` go to `outputs/kerala-groom/`. No source photograph is embedded in or distributed with the asset. The existing environment continues to use Kenney assets; this custom character is authored in Blender.

An earlier version used the user-supplied `D:\dulquer_salmaan_3d_model.glb`. `prepare_supplied_character.py` removes unrelated scene geometry, caps embedded texture sizes for phones, and exports `dist/assets/wedding-character.glb`. That source rig has no animation clips and was replaced because procedural walking did not look natural.

`dist/character.js` loads the skinned GLB, normalizes its height to 1.65 world units, and blends Idle/Walk based on actual distance traveled. It resets the walk pose when a details panel pauses movement. The model faces glTF +Z, matching the game's movement heading. The old primitive avatar and duplicate static arms have been removed.

Validation: rendered front and three-quarter Blender previews; checked the GLB in Three.js; tested opposite arm swings, arm/leg counter-swing, returning to idle on pause, mobile layouts at 390×844 and 320×740, arrival details and the Directions fallback. Final model: about 25,000 triangles, 12 material draws, approximately 1 MB without external textures.

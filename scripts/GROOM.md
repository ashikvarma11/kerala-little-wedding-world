# Kerala groom character

The character is an original stylized Blender model based on the user-supplied portrait. The warm medium skin, pale ivory band-collar kurta, rolled sleeves, gold kasavu mundu, dark swept hair, beard and black bracelet follow that reference. The unseen back and feet are interpreted; simple brown sandals complete the model. The likeness is approximate, not a photogrammetry scan.

`build_groom.py` creates the mesh, 12-bone skeleton, Idle and Walk clips, GLB, editable Blender file and studio review images. Run from the repository root with Blender 4.5:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe' --background --python scripts/build_groom.py
```

The runtime GLB is written to `dist/assets/kerala-groom.glb`; review images and `kerala-groom.blend` go to `outputs/kerala-groom/`. No source photograph is embedded in or distributed with the asset. The existing environment continues to use Kenney assets; this custom character is authored in Blender.

The live game currently uses the later user-supplied `D:\dulquer_salmaan_3d_model.glb`. `prepare_supplied_character.py` removes unrelated scene geometry, caps embedded texture sizes for phones, and exports `dist/assets/wedding-character.glb`. Because that source rig has no animation clips, `dist/character.js` drives its existing arm, forearm, hip, knee, spine, and pelvis bones during play.

`dist/character.js` loads the skinned GLB, normalizes its height to 1.65 world units, and blends Idle/Walk based on actual distance traveled. It resets the walk pose when a details panel pauses movement. The model faces glTF +Z, matching the game's movement heading. The old primitive avatar and duplicate static arms have been removed.

Validation: rendered front and three-quarter Blender previews; checked the GLB in Three.js; tested opposite arm swings, arm/leg counter-swing, returning to idle on pause, mobile layouts at 390×844 and 320×740, arrival details and the Directions fallback. Final model: about 25,000 triangles, 12 material draws, approximately 1 MB without external textures.

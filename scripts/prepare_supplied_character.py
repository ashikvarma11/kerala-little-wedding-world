"""Prepare the user-supplied rigged GLB for the mobile wedding world."""
import bpy, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = r'D:\dulquer_salmaan_3d_model.glb'
TARGET = os.path.join(ROOT, 'dist', 'assets', 'wedding-character.glb')

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.images, bpy.data.armatures):
    for block in list(datablocks):
        if block.users == 0:
            datablocks.remove(block)

bpy.ops.import_scene.gltf(filepath=SOURCE)

# The source includes an unrelated low-poly Icosphere; retain the avatar hierarchy.
for obj in list(bpy.context.scene.objects):
    if obj.name == 'Icosphere':
        bpy.data.objects.remove(obj, do_unlink=True)

# Cap embedded textures for a faster first load on phones while preserving the face and outfit.
for image in bpy.data.images:
    if image.size[0] > 768 or image.size[1] > 768:
        ratio = min(768 / image.size[0], 768 / image.size[1])
        image.scale(max(1, round(image.size[0] * ratio)), max(1, round(image.size[1] * ratio)))

for obj in bpy.context.scene.objects:
    obj.select_set(obj.type in {'MESH', 'ARMATURE', 'EMPTY'})

bpy.ops.export_scene.gltf(
    filepath=TARGET,
    export_format='GLB',
    use_selection=True,
    export_animations=False,
    export_image_format='AUTO',
    export_jpeg_quality=82,
    export_apply=False,
)
print('PREPARED', TARGET, os.path.getsize(TARGET))

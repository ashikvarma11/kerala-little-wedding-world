"""Create an original, stylized reference-based Kerala groom in Blender 4.5.
Run: blender --background --python scripts/build_groom.py
The photo informs the palette and clothing; no photograph is embedded in the asset.
"""
import bpy, math, os, json
from mathutils import Vector
from math import sin, cos, pi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'outputs', 'kerala-groom')
os.makedirs(OUT, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
parts = []

def material(name, hexcolor, rough=.6, metallic=0):
    rgb = [int(hexcolor[i:i+2],16)/255 for i in (0,2,4)]
    rgb = [v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    m=bpy.data.materials.new(name); m.diffuse_color=(*rgb,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metallic
    return m
skin=material('Warm medium skin • reference', 'AA7557', .57)
skinlight=material('Lips and ear warmth', 'A36550', .6)
ivory=material('Pale ivory silk kurta', 'E6E6D1', .42)
cloth=material('Ivory cotton mundu', 'F0EDDC', .76)
seam=material('Silk seams and folds', 'D3D4B9', .52)
gold=material('Kasavu woven gold', 'C9A147', .37, .55)
hair=material('Black brown hair', '201A18', .72)
hairglint=material('Swept hair ridges', '302622', .72)
white=material('Warm eye white', 'EDE8DD', .5)
iris=material('Dark brown iris', '422A21', .5)
black=material('Pupils', '141313', .5)
leather=material('Brown sandal leather', '533729', .8)

def finish(o,name,mat,bone):
    o.name=name; o.data.materials.append(mat)
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for p in o.data.polygons: p.use_smooth=True
    group=o.vertex_groups.new(name=bone); group.add(list(range(len(o.data.vertices))),1,'REPLACE')
    parts.append(o); return o

def ell(name,loc,scale,mat,bone='Spine',seg=20,rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=loc)
    o=bpy.context.object; o.scale=scale; return finish(o,name,mat,bone)

def tube(name,points,radius,mat,bone='Spine'):
    curve=bpy.data.curves.new(name,'CURVE'); curve.dimensions='3D'; curve.resolution_u=2
    curve.bevel_depth=radius; curve.bevel_resolution=2
    s=curve.splines.new('POLY'); s.points.add(len(points)-1)
    for p,v in zip(s.points,points): p.co=(*v,1)
    o=bpy.data.objects.new(name,curve); bpy.context.collection.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH'); return finish(o,name,mat,bone)

def rings_mesh(name,rows,mat,bone,n=40,pleat=0):
    # rows: height, width radius, depth radius, center y
    verts=[]
    for z,rx,ry,cy in rows:
        for i in range(n):
            a=2*pi*i/n; fold=1+pleat*cos(12*a)
            verts.append((rx*cos(a)*fold,cy+ry*sin(a)*fold,z))
    faces=[]
    for j in range(len(rows)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces += [tuple(reversed(range(n))),tuple((len(rows)-1)*n+i for i in range(n))]
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);finish(o,name,mat,bone);return o

# Long, softly tapered kurta and wrapped mundu, front is Blender -Y.
kurta=rings_mesh('Silk kurta with flared knee hem',[(.64,.245,.148,0),(.69,.248,.15,0),(.82,.232,.145,0),(.98,.21,.132,0),(1.13,.217,.14,0),(1.31,.258,.145,0),(1.39,.24,.12,0),(1.445,.105,.085,0)],ivory,'Spine',48,.009)
dhoti=rings_mesh('Full length mundu with vertical cloth folds',[(.09,.23,.14,0),(.13,.24,.144,0),(.3,.233,.143,0),(.5,.22,.14,0),(.72,.208,.133,0),(.96,.19,.125,0)],cloth,'Pelvis',64,.028)
# Kasavu border follows the front wrap and flares gently toward the ankles.
verts=[]
for z in [.105,.2,.3,.4,.5,.58,.635]:
    x=-.07-.025*(.94-z); y=-.148
    for off in [-.021,.021]:verts.append((x+off,y,z))
me=bpy.data.meshes.new('Kasavu border');me.from_pydata(verts,[],[(2*i,2*i+1,2*i+3,2*i+2) for i in range(6)]);me.update()
o=bpy.data.objects.new('Wide gold kasavu border',me);bpy.context.collection.objects.link(o);finish(o,o.name,gold,'Pelvis')
for offset in [-.028,.028]:tube('Fine woven border piping',[(-.07-.025*(.94-z)+offset,-.15,z) for z in [.11,.3,.5,.635]],.0023,gold,'Pelvis')
for i in range(7):
    x=.005+i*.017;tube('Front mundu pleat',[(x,-.145,.14),(x*.82,-.149,.38),(x*.7,-.143,.63)],.0025,seam,'Pelvis')
tube('Kurta lower hem',[(.247*cos(a),.152*sin(a),.663) for a in [2*pi*i/80 for i in range(81)]],.004,seam)
ell('Neck',(0,0,1.47),(.084,.075,.102),skin,'Head')
rings_mesh('Standing band collar',[(1.414,.108,.088,0),(1.461,.105,.084,0)],ivory,'Spine',40)
for x in [-.013,.013]:tube('Button placket',[(x,-.09,1.443),(x,-.136,1.36),(x,-.146,1.23)],.0035,seam)
for z in [1.398,1.342,1.286]:ell('Mother of pearl button',(0,-.151,z),(.008,.004,.008),gold,seg=10,rings=6)
for s in [-1,1]:
    # Silhouette folds give the silk shape without photo textures.
    for j in range(3):
        z=.78+j*.16;tube('Soft diagonal silk fold',[(s*.13,-.118,z),(s*.17,-.097,z+.014),(s*.20,-.072,z+.022)],.0015,seam)
    side='L' if s<0 else 'R'
    upper='UpperArm_'+side; lower='Forearm_'+side
    sleeve=rings_mesh('Tailored kurta sleeve',[(1.105,.055,.056,0),(1.17,.062,.064,0),(1.28,.069,.072,0),(1.35,.073,.076,0),(1.385,.053,.058,0)],ivory,upper,32)
    sleeve.location.x=s*.274
    ell('Sleeve forearm',(s*.296,-.015,1.104),(.060,.059,.075),ivory,lower)
    for z in [1.077,1.091,1.105]:tube('Rolled sleeve cuff',[(s*.296+.06*cos(a),-.015+.06*sin(a),z) for a in [2*pi*i/24 for i in range(25)]],.007,ivory,lower)
    ell('Visible forearm',(s*.3,-.017,1.008),(.042,.043,.085),skin,lower)
    ell('Palm',(s*.303,-.021,.917),(.044,.032,.065),skin,lower)
    for j in range(4):ell('Finger',(s*(.277+j*.016),-.029,.868+abs(j-1.5)*.004),(.009,.014,.036),skin,lower,12,8)
    thumb=ell('Thumb',(s*.263,-.04,.916),(.014,.017,.034),skin,lower,12,8);thumb.rotation_euler.y=s*.4
    if s<0:
        for j in range(14):
            a=j*2*pi/14;ell('Black bead bracelet',(s*.30+.044*cos(a),-.017+.044*sin(a),.962),(.009,.009,.009),black,lower,8,6)
    ell('Ankle',(s*.105,0,.12),(.05,.059,.095),skin,'Shin_'+side)
    ell('Leather sandal sole',(s*.108,-.047,.04),(.07,.133,.025),leather,'Shin_'+side)
    ell('Foot',(s*.108,-.054,.069),(.061,.108,.038),skin,'Shin_'+side)
    tube('Sandal strap',[(s*.108-.057,-.09,.07),(s*.108,-.077,.105),(s*.108+.057,-.09,.07)],.012,leather,'Shin_'+side)

# Face contours, shaped hairline and groomed beard.
head=rings_mesh('Sculpted face',[(1.47,.048,.059,-.015),(1.49,.086,.09,-.009),(1.53,.12,.108,0),(1.58,.14,.115,0),(1.64,.143,.116,0),(1.70,.135,.11,.004),(1.76,.111,.09,.006),(1.79,.052,.044,.008)],skin,'Head',48)
for s in [-1,1]:
    ell('Ear',(s*.143,0,1.611),(.026,.026,.053),skin,'Head')
    ell('Ear concha',(s*.159,-.017,1.61),(.01,.009,.027),skinlight,'Head',12,8)
    # Almond shaped whites are shallow, inset against the face.
    ell('Eye white',(s*.058,-.112,1.653),(.028,.006,.010),white,'Head')
    ell('Brown iris',(s*.058,-.118,1.652),(.009,.003,.009),iris,'Head',16,10)
    ell('Pupil',(s*.058,-.121,1.652),(.0045,.001,.0055),black,'Head',12,8)
    ell('Eye highlight',(s*.055,-.122,1.655),(.0015,.001,.0015),white,'Head',8,6)
    tube('Upper eyelid',[(s*.029,-.109,1.653),(s*.046,-.114,1.661),(s*.067,-.11,1.662),(s*.084,-.101,1.654)],.0025,skinlight,'Head')
    tube('Dark eyebrow',[(s*.025,-.105,1.686),(s*.047,-.115,1.693),(s*.073,-.108,1.69),(s*.091,-.098,1.681)],.006,hair,'Head')
ell('Nose bridge',(0,-.112,1.628),(.019,.021,.043),skin,'Head')
ell('Nose tip',(0,-.14,1.608),(.023,.022,.017),skin,'Head')
for s in [-1,1]:
    ell('Nostril wing',(s*.019,-.128,1.601),(.015,.014,.012),skin,'Head',16,10)
    ell('Nostril',(s*.015,-.14,1.594),(.006,.005,.003),skinlight,'Head',12,6)

# Beard hugs the cheek and jaw instead of covering the mouth.
verts=[];faces=[]
for j in range(5):
    t=j/4
    for i in range(49):
        a=pi*2*i/48; front=max(0,-sin(a)); side=abs(cos(a))
        top=1.565+.055*side
        bottom=1.478+.008*side
        z=bottom+(top-bottom)*t
        profiles=[(1.47,.048,.059,-.015),(1.49,.086,.09,-.009),(1.53,.12,.108,0),(1.58,.14,.115,0),(1.64,.143,.116,0)]
        for low,high in zip(profiles,profiles[1:]):
            if low[0]<=z<=high[0]:
                k=(z-low[0])/(high[0]-low[0]);rx=low[1]+(high[1]-low[1])*k;ry=low[2]+(high[2]-low[2])*k;cy=low[3]+(high[3]-low[3])*k;break
        verts.append(((rx+.0025)*cos(a),(ry+.0025)*sin(a)+cy,z))
for j in range(4):
    for i in range(48):faces.append((j*49+i,j*49+i+1,(j+1)*49+i+1,(j+1)*49+i))
me=bpy.data.meshes.new('Short beard surface');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Trimmed beard',me);bpy.context.collection.objects.link(o);finish(o,o.name,hair,'Head')
for s in [-1,1]:tube('Moustache',[(0,-.12,1.582),(s*.018,-.126,1.582),(s*.035,-.121,1.576),(s*.047,-.112,1.569)],.008,hair,'Head')
tube('Smile lip',[(-.044,-.117,1.564),(-.022,-.13,1.554),(0,-.134,1.551),(.022,-.13,1.554),(.044,-.117,1.564)],.0045,skinlight,'Head')
tube('Subtle smiling teeth',[(-.029,-.128,1.563),(0,-.135,1.558),(.029,-.128,1.563)],.0035,white,'Head')
# Hair cap with lower sides/back and higher front hairline.
verts=[];faces=[]
for j in range(13):
    for i in range(49):
        a=2*pi*i/48; front=max(0,-sin(a)); theta=(j/12)*(1.73-.64*front)
        sweep=.026*max(0,-sin(a))*sin(theta)*(1-.5*cos(a))
        verts.append((.146*sin(theta)*cos(a),.119*sin(theta)*sin(a)+.011,1.689+.135*cos(theta)+sweep))
for j in range(12):
    for i in range(48):faces.append((j*49+i,j*49+i+1,(j+1)*49+i+1,(j+1)*49+i))
me=bpy.data.meshes.new('Hair cap');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Side parted black hair',me);bpy.context.collection.objects.link(o);finish(o,o.name,hair,'Head')
for i in range(9):
    points=[]
    for j in range(18):
        t=j/17;theta=.25+t*.72;a=-2.35+i*.19+t*.14
        points.append((.147*sin(theta)*cos(a),.120*sin(theta)*sin(a)+.011,1.689+.136*cos(theta)+.026*max(0,-sin(a))*sin(theta)*(1-.5*cos(a))))
    tube('Combed side swept texture',points,.0018,hairglint,'Head')

# One skinned mesh, small material palette, no image downloads.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();body=bpy.context.object;body.name='Groom_SkinnedMesh'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
armdata=bpy.data.armatures.new('Kerala_Groom_Rig');rig=bpy.data.objects.new('Kerala_Groom_Rig',armdata);bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;body.select_set(False);rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def bone(name,head,tail,parent=None):
    b=armdata.edit_bones.new(name);b.head=head;b.tail=tail
    if parent:b.parent=armdata.edit_bones[parent]
bone('Root',(0,0,0),(0,0,.2))
bone('Pelvis',(0,0,.94),(0,0,1.08),'Root')
bone('Spine',(0,0,1.08),(0,0,1.43),'Pelvis')
bone('Head',(0,0,1.43),(0,0,1.75),'Spine')
for s in [-1,1]:
    side='L' if s<0 else 'R'
    bone('UpperArm_'+side,(s*.25,0,1.37),(s*.295,0,1.14),'Spine')
    bone('Forearm_'+side,(s*.295,0,1.14),(s*.303,-.02,.92),'UpperArm_'+side)
    bone('Thigh_'+side,(s*.105,0,.94),(s*.105,0,.5),'Pelvis')
    bone('Shin_'+side,(s*.105,0,.5),(s*.105,0,.12),'Thigh_'+side)
bpy.ops.object.mode_set(mode='OBJECT')
body.parent=rig;mod=body.modifiers.new('Skin to walking skeleton','ARMATURE');mod.object=rig
# Keep the continuous mundu drape; walking feet take small steps beneath it.
for p in rig.pose.bones:p.rotation_mode='XYZ'
bpy.context.scene.render.fps=30
for f in range(1,34,2):
    a=(f-1)/32*2*pi
    for s in [-1,1]:
        side='L' if s<0 else 'R'; wave=sin(a)*s
        for name,angle in [('UpperArm_',-.35*wave),('Forearm_',-.06-.10*max(0,wave)),('Thigh_',.10*wave),('Shin_',max(0,-wave)*.10)]:
            p=rig.pose.bones[name+side];p.rotation_euler.x=angle;p.keyframe_insert('rotation_euler',frame=f,group=p.name)
    p=rig.pose.bones['Spine'];p.rotation_euler.y=.018*sin(a);p.keyframe_insert('rotation_euler',frame=f,group=p.name)
    p=rig.pose.bones['Pelvis'];p.location.y=.008*(1-cos(2*a));p.keyframe_insert('location',frame=f,group=p.name)
walk=rig.animation_data.action;walk.name='Walk'
rig.animation_data.action=None
for p in rig.pose.bones:p.rotation_euler=(0,0,0);p.location=(0,0,0)
for f in [1,31,61]:
    p=rig.pose.bones['Spine'];p.rotation_euler.x=.006 if f==31 else 0;p.keyframe_insert('rotation_euler',frame=f,group=p.name)
idle=rig.animation_data.action;idle.name='Idle'
rig.animation_data.action=None
for p in rig.pose.bones:p.rotation_euler=(0,0,0);p.location=(0,0,0)
scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=33;scene.frame_set(1)
rig['reference_notes']='Stylized interpretation of supplied portrait; ivory kurta, gold kasavu mundu, warm skin, swept hair, beard. Sandals inferred because reference feet are obscured.'
rig['front']='Blender -Y, glTF +Z'
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);rig.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'dist','assets','kerala-groom.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True)

# Save a reusable Blender source with studio lighting and review cameras.
scene.render.engine='CYCLES';scene.cycles.samples=32
scene.world.color=(.16,.16,.16)
stage=material('Studio backdrop','324B47',.9)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.005));floor=bpy.context.object;floor.name='Studio floor';floor.data.materials.append(stage)
def area(name,loc,power,size):
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
area('Large softbox',(-3,-4,5),450,4);area('Fill',(3,-1,3),230,3);area('Rim',(1,3,4),500,3)
bpy.ops.object.camera_add(location=(2.8,-5,2.65));camera=bpy.context.object;camera.name='Portrait review camera';camera.rotation_euler=(Vector((0,0,.95))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=2.1;scene.camera=camera
scene.render.resolution_x=800;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'kerala-groom.blend'))
scene.render.filepath=os.path.join(OUT,'groom-preview.png');bpy.ops.render.render(write_still=True)
camera.location=(0,-5,1.15);camera.rotation_euler=(Vector((0,0,1.1))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=os.path.join(OUT,'groom-front.png');bpy.ops.render.render(write_still=True)
triangles=sum(len(p.vertices)-2 for p in body.data.polygons)
with open(os.path.join(OUT,'model-info.json'),'w') as f:json.dump({'triangles':triangles,'bones':len(armdata.bones),'animations':['Idle','Walk'],'glb_bytes':os.path.getsize(os.path.join(ROOT,'dist','assets','kerala-groom.glb'))},f,indent=2)
print('GROOM COMPLETE',triangles,'triangles')

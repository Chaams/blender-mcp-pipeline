"""Exécuté DANS Blender :  blender -b <fichier.blend> -P render_turntable.py -- <out_dir> <frames> <size_px>

Fait tourner les meshes de la scène sur 360° (rendu Workbench, rapide, sans carte graphique dédiée)
et écrit frame_0000.png, frame_0001.png… dans out_dir.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
out_dir, frames, size = Path(args[0]), int(args[1]), int(args[2])
out_dir.mkdir(parents=True, exist_ok=True)

scene = bpy.context.scene
meshes = [o for o in scene.objects if o.type == "MESH"]
if not meshes:
    raise SystemExit("aucun mesh dans la scène")

# Couleur « bois » pour que l'asset soit lisible en rendu Workbench
for obj in meshes:
    for mat in obj.data.materials:
        if mat:
            mat.diffuse_color = (0.62, 0.40, 0.20, 1.0)

scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_cavity = True
scene.render.resolution_x = scene.render.resolution_y = size
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.color = (0.07, 0.08, 0.06)

# Cadrage d'après la boîte englobante
corners = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
center = sum(corners, Vector()) / len(corners)
radius = max((c - center).length for c in corners)

target = bpy.data.objects.new("Target", None)
scene.collection.objects.link(target)
target.location = center

cam_data = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam)
cam.location = center + Vector((radius * 2.6, -radius * 2.6, radius * 1.7))
track = cam.constraints.new("TRACK_TO")
track.target, track.track_axis, track.up_axis = target, "TRACK_NEGATIVE_Z", "UP_Y"
scene.camera = cam

for i in range(frames):
    for obj in meshes:
        obj.rotation_euler[2] = 2 * math.pi * i / frames
    scene.render.filepath = str(out_dir / f"frame_{i:04d}.png")
    bpy.ops.render.render(write_still=True)
print(f"TURNTABLE_FRAMES={frames}")

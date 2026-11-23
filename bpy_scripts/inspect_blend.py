"""Exécuté DANS Blender :  blender -b <fichier.blend> -P inspect_blend.py

Affiche une ligne « ASSETS_JSON=[...] » : un descripteur par objet mesh de la scène.
"""
import json

import bpy

assets = []
for obj in bpy.context.scene.objects:
    if obj.type != "MESH":
        continue
    mesh = obj.data
    mesh.calc_loop_triangles()
    textures = []
    for mat in mesh.materials:
        if mat and mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image:
                    textures.append({"name": node.image.name.rsplit(".", 1)[0],
                                     "width": node.image.size[0], "height": node.image.size[1]})
    assets.append({
        "name": obj.name,
        "kind": "static_mesh",
        "tri_count": len(mesh.loop_triangles),
        "has_uv": len(mesh.uv_layers) > 0,
        "materials": len([m for m in mesh.materials if m]),
        "scale": [round(s, 6) for s in obj.scale],
        "dimensions": [round(d, 4) for d in obj.dimensions],
        "textures": textures,
    })
print("ASSETS_JSON=" + json.dumps(assets))

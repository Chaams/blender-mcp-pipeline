"""Exécuté DANS Blender :  blender -b -P make_prop.py -- <kind> <size_m> <out_dir> <name>

Génère un prop procédural (caisse ou tonneau) propre pour un moteur de jeu : UV dépliées, échelle appliquée,
un matériau, normales cohérentes. Exporte <name>.fbx et <name>.blend, puis écrit <name>.asset.json
(descripteur validé ensuite par game-asset-validator).
"""
import json
import sys
from pathlib import Path

import bpy
import bmesh

argv = sys.argv[sys.argv.index("--") + 1:]
kind, size, out_dir, name = argv[0], float(argv[1]), Path(argv[2]), argv[3]
out_dir.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)

if kind == "crate":
    bpy.ops.mesh.primitive_cube_add(size=size)
elif kind == "barrel":
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=size * 0.4, depth=size)
else:
    raise SystemExit(f"kind inconnu : {kind}")

obj = bpy.context.active_object
obj.name = name
obj.data.name = name

# Bevel pour casser les arêtes vives, puis application des modifieurs et de l'échelle
bevel = obj.modifiers.new("Bevel", "BEVEL")
bevel.width = size * 0.03
bevel.segments = 2
bpy.ops.object.modifier_apply(modifier="Bevel")
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Dépliage UV
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
bpy.ops.object.mode_set(mode="OBJECT")

# Matériau
mat = bpy.data.materials.new(f"M_{name[3:] if name.startswith('SM_') else name}")
mat.use_nodes = True
obj.data.materials.append(mat)

# Descripteur d'asset
mesh = obj.data
mesh.calc_loop_triangles()
descriptor = {
    "name": name,
    "kind": "static_mesh",
    "tri_count": len(mesh.loop_triangles),
    "has_uv": len(mesh.uv_layers) > 0,
    "materials": len(mesh.materials),
    "scale": [round(s, 6) for s in obj.scale],
    "dimensions": [round(d, 4) for d in obj.dimensions],
    "textures": [],
}

bpy.ops.export_scene.fbx(filepath=str(out_dir / f"{name}.fbx"), use_selection=True,
                         apply_scale_options="FBX_SCALE_ALL", object_types={"MESH"})
bpy.ops.wm.save_as_mainfile(filepath=str(out_dir / f"{name}.blend"))
(out_dir / f"{name}.asset.json").write_text(json.dumps(descriptor, indent=2), encoding="utf-8")
print("ASSET_JSON=" + json.dumps(descriptor))

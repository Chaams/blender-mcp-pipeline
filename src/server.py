"""Serveur MCP « blender-pipeline » : génère, inspecte et valide des assets Blender pour un jeu.

Lancer :  python -m src.server     (transport stdio, à déclarer dans un client MCP : Claude, IDE…)
"""
from __future__ import annotations

from game_asset_validator import validate
from mcp.server.fastmcp import FastMCP

from . import blender_runner

mcp = FastMCP("blender-pipeline")


@mcp.tool()
def generate_prop(kind: str, name: str, out_dir: str, size: float = 1.0) -> dict:
    """Génère un prop procédural prêt pour un moteur (UV, échelle appliquée, FBX + .blend).

    kind : « crate » ou « barrel ». name : nom d'asset, ex. SM_WoodenCrate."""
    return blender_runner.make_prop(kind, size, out_dir, name)


@mcp.tool()
def inspect_blend(path: str) -> list[dict]:
    """Liste les meshes d'un .blend (triangles, UV, matériaux, échelle, dimensions, textures)."""
    return blender_runner.inspect_blend(path)


@mcp.tool()
def validate_blend(path: str, profile: str = "pc") -> list[dict]:
    """Valide chaque mesh d'un .blend contre un profil (mobile | pc | hero) et renvoie les problèmes."""
    return [validate(asset, profile).to_dict() for asset in blender_runner.inspect_blend(path)]


@mcp.tool()
def render_turntable(blend_path: str, out_gif: str, frames: int = 24, size: int = 360) -> dict:
    """Rend une rotation à 360° de l'asset (Blender Workbench) et écrit un GIF animé, pour une démo ou une revue."""
    return blender_runner.render_turntable(blend_path, out_gif, frames, size)


if __name__ == "__main__":
    mcp.run()

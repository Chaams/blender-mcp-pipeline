"""Lance Blender en arrière-plan (sans interface) et récupère les résultats JSON."""
from __future__ import annotations

import glob
import json
import os
import subprocess
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "bpy_scripts"


class BlenderNotFound(RuntimeError):
    pass


def find_blender() -> str:
    """BLENDER_PATH, sinon emplacements habituels (Windows, macOS, Linux)."""
    env = os.environ.get("BLENDER_PATH")
    if env and Path(env).exists():
        return env
    candidates = (
        glob.glob(r"C:\Program Files\Blender Foundation\*\blender.exe")
        + glob.glob("/Applications/Blender.app/Contents/MacOS/Blender")
        + glob.glob("/usr/bin/blender") + glob.glob("/snap/bin/blender")
    )
    if candidates:
        return sorted(candidates)[-1]
    raise BlenderNotFound("Blender introuvable : définissez la variable d'environnement BLENDER_PATH")


def run_blender(args: list[str], timeout: int = 180) -> str:
    proc = subprocess.run([find_blender(), "-b", *args], capture_output=True, text=True, timeout=timeout,
                          stdin=subprocess.DEVNULL)  # sans cela, Blender lit le canal MCP du serveur parent
    if proc.returncode != 0:
        raise RuntimeError(f"Blender a échoué ({proc.returncode}) :\n{proc.stdout[-800:]}\n{proc.stderr[-800:]}")
    return proc.stdout


def _marker(stdout: str, marker: str):
    for line in stdout.splitlines():
        if line.startswith(marker):
            return json.loads(line[len(marker):])
    raise RuntimeError(f"{marker} absent de la sortie de Blender")


def make_prop(kind: str, size: float, out_dir: str, name: str) -> dict:
    out = run_blender(["-P", str(SCRIPTS / "make_prop.py"), "--", kind, str(size), out_dir, name])
    return _marker(out, "ASSET_JSON=")


def inspect_blend(path: str) -> list[dict]:
    out = run_blender([path, "-P", str(SCRIPTS / "inspect_blend.py")])
    return _marker(out, "ASSETS_JSON=")

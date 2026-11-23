# blender-mcp-pipeline

Serveur **MCP** qui pilote **Blender** (mode `-b`, sans interface) pour produire et contrôler des assets de jeu :

| Outil MCP | Rôle |
|---|---|
| `generate_prop(kind, name, out_dir, size)` | Crée une caisse ou un tonneau : bevel, UV dépliées, échelle appliquée, matériau, export FBX + `.blend` |
| `inspect_blend(path)` | Extrait triangles, UV, matériaux, échelle, dimensions, textures de chaque mesh |
| `validate_blend(path, profile)` | Valide chaque mesh (profils `mobile` / `pc` / `hero`) via [game-asset-validator](https://github.com/Chaams/game-asset-validator) |

| `render_turntable(blend_path, out_gif, frames, size)` | Rend une rotation à 360° (Blender Workbench) et assemble un GIF animé pour une démo ou une revue |

![Tonneau généré par le serveur MCP puis rendu par Blender](docs/demo-turntable.gif)

*Asset `SM_OilBarrel` généré par `generate_prop` et rendu par `render_turntable`, tous deux appelés via MCP.*

Le code qui s'exécute dans Blender est dans `bpy_scripts/` ; `src/blender_runner.py` le lance et lit le JSON renvoyé.

## Installer et lancer

```bash
pip install -r requirements.txt
set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.1\blender.exe   # sinon détection automatique
pytest -v          # 6 tests d'intégration avec le vrai Blender (ignorés si Blender est absent)
python -m src.server
```

Déclaration dans un client MCP :

```json
{ "mcpServers": { "blender-pipeline": { "command": "python", "args": ["-m", "src.server"] } } }
```

Testé avec Blender 4.1.

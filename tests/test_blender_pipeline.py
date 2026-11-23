"""Tests d'intégration : exécutent le vrai Blender. Ignorés automatiquement si Blender est absent (ex. CI)."""
from pathlib import Path

import pytest
from game_asset_validator import validate

from src import blender_runner

try:
    blender_runner.find_blender()
    HAS_BLENDER = True
except blender_runner.BlenderNotFound:
    HAS_BLENDER = False

pytestmark = pytest.mark.skipif(not HAS_BLENDER, reason="Blender non installé")


def test_find_blender_returns_existing_path():
    assert Path(blender_runner.find_blender()).exists()


@pytest.mark.parametrize("kind,name", [("crate", "SM_WoodenCrate"), ("barrel", "SM_OilBarrel")])
def test_generated_prop_is_game_ready(tmp_path, kind, name):
    asset = blender_runner.make_prop(kind, 1.0, str(tmp_path), name)
    assert (tmp_path / f"{name}.fbx").stat().st_size > 0
    assert (tmp_path / f"{name}.blend").exists()
    report = validate(asset, "mobile")
    assert report.ok, report.issues
    assert asset["has_uv"] and asset["scale"] == [1.0, 1.0, 1.0]


def test_inspect_roundtrip_matches_generation(tmp_path):
    generated = blender_runner.make_prop("crate", 2.0, str(tmp_path), "SM_BigCrate")
    inspected = blender_runner.inspect_blend(str(tmp_path / "SM_BigCrate.blend"))
    assert len(inspected) == 1
    assert inspected[0]["tri_count"] == generated["tri_count"]
    assert inspected[0]["dimensions"] == pytest.approx(generated["dimensions"], abs=1e-3)


def test_bad_name_is_flagged_after_generation(tmp_path):
    asset = blender_runner.make_prop("crate", 1.0, str(tmp_path), "wooden_crate")
    assert "NAME_PREFIX" in {i.code for i in validate(asset).issues}

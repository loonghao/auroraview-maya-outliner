"""Verify the backend, built frontend and maintained tutorial recipe inputs."""

import sys
import zipfile

required = (
    "maya-outliner/auroraview_maya_outliner/__init__.py",
    "maya-outliner/auroraview_maya_outliner/maya_outliner.py",
    "maya-outliner/auroraview_maya_outliner/scene.py",
    "maya-outliner/auroraview_maya_outliner/config.py",
    "maya-outliner/dist/index.html",
    "maya-outliner/maya-outliner.mod",
    "maya-outliner/README.md",
    "maya-outliner/README_zh.md",
    "maya-outliner/docs/PROVENANCE.md",
    "maya-outliner/justfile",
    "maya-outliner/vx.toml",
    "maya-outliner/package.json",
    "maya-outliner/package-lock.json",
    "maya-outliner/.npmrc",
    "maya-outliner/index.html",
    "maya-outliner/vite.config.ts",
    "maya-outliner/tsconfig.json",
    "maya-outliner/tailwind.config.cjs",
    "maya-outliner/postcss.config.cjs",
    "maya-outliner/components.json",
    "maya-outliner/pytest.ini",
    "maya-outliner/build_maya_package.py",
    "maya-outliner/build_utils.py",
    "maya-outliner/src/App.vue",
    "maya-outliner/scripts/run_maya_smoke.py",
    "maya-outliner/scripts/maya_smoke.py",
    "maya-outliner/scripts/verify_package.py",
    "maya-outliner/tests/test_scene.py",
    "maya-outliner/tests/test_lifecycle.py",
)
with zipfile.ZipFile(sys.argv[1]) as archive:
    missing = set(required) - set(archive.namelist())
    if missing:
        raise SystemExit("Missing demo files: {}".format(sorted(missing)))
    assert any("/dist/assets/" in name and name.endswith(".js") for name in archive.namelist())
    assert "MAYAVERSION:2026" in archive.read("maya-outliner/maya-outliner.mod").decode("utf-8")
    recipes = archive.read("maya-outliner/justfile").decode("utf-8")
    assert "maya-runtime mayapy target:" in recipes
    assert "maya-smoke mayapy:" in recipes
print("Source demo archive verified (runtime installation is separate).")

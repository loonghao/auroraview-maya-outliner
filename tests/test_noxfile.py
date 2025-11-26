"""Tests for build utilities package building functions."""

import sys
from pathlib import Path


# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from build_utils import create_mod_file, create_production_usersetup


class TestCreateModFile:
    """Test create_mod_file function."""

    def test_mod_file_created(self, tmp_path: Path) -> None:
        """Test that mod file is created."""
        create_mod_file(tmp_path, "1.0.0")
        mod_file = tmp_path / "maya-outliner.mod"
        assert mod_file.exists()

    def test_mod_file_contains_version(self, tmp_path: Path) -> None:
        """Test that mod file contains the version."""
        create_mod_file(tmp_path, "2.5.0")
        mod_file = tmp_path / "maya-outliner.mod"
        content = mod_file.read_text()
        assert "2.5.0" in content

    def test_mod_file_contains_pythonpath(self, tmp_path: Path) -> None:
        """Test that mod file contains PYTHONPATH directive."""
        create_mod_file(tmp_path, "1.0.0")
        mod_file = tmp_path / "maya-outliner.mod"
        content = mod_file.read_text()
        assert "PYTHONPATH +:= ./" in content

    def test_mod_file_contains_scripts_directive(self, tmp_path: Path) -> None:
        """Test that mod file contains scripts directive."""
        create_mod_file(tmp_path, "1.0.0")
        mod_file = tmp_path / "maya-outliner.mod"
        content = mod_file.read_text()
        assert "scripts: ./" in content

    def test_mod_file_supports_maya_versions(self, tmp_path: Path) -> None:
        """Test that mod file supports Maya 2022, 2024, 2025."""
        create_mod_file(tmp_path, "1.0.0")
        mod_file = tmp_path / "maya-outliner.mod"
        content = mod_file.read_text()
        assert "MAYAVERSION:2022" in content
        assert "MAYAVERSION:2024" in content
        assert "MAYAVERSION:2025" in content


class TestCreateProductionUsersetup:
    """Test create_production_usersetup function."""

    def test_usersetup_created(self, tmp_path: Path) -> None:
        """Test that userSetup.py is created."""
        create_production_usersetup(tmp_path)
        usersetup_file = tmp_path / "userSetup.py"
        assert usersetup_file.exists()

    def test_usersetup_no_project_root_template(self, tmp_path: Path) -> None:
        """Test that userSetup.py doesn't contain PROJECT_ROOT template."""
        create_production_usersetup(tmp_path)
        usersetup_file = tmp_path / "userSetup.py"
        content = usersetup_file.read_text(encoding="utf-8")
        # Should not contain the template placeholder
        assert "{{PROJECT_ROOT}}" not in content

    def test_usersetup_imports_maya_modules(self, tmp_path: Path) -> None:
        """Test that userSetup.py imports maya modules."""
        create_production_usersetup(tmp_path)
        usersetup_file = tmp_path / "userSetup.py"
        content = usersetup_file.read_text(encoding="utf-8")
        assert "import maya.utils" in content
        assert "from maya import cmds" in content

    def test_usersetup_imports_auroraview_maya_outliner(self, tmp_path: Path) -> None:
        """Test that userSetup.py imports auroraview_maya_outliner."""
        create_production_usersetup(tmp_path)
        usersetup_file = tmp_path / "userSetup.py"
        content = usersetup_file.read_text(encoding="utf-8")
        assert "from auroraview_maya_outliner import maya_outliner" in content

    def test_usersetup_creates_shelf_button(self, tmp_path: Path) -> None:
        """Test that userSetup.py creates shelf button."""
        create_production_usersetup(tmp_path)
        usersetup_file = tmp_path / "userSetup.py"
        content = usersetup_file.read_text(encoding="utf-8")
        assert "shelfButton" in content
        assert "AuroraView" in content

    def test_usersetup_shelf_command_simple(self, tmp_path: Path) -> None:
        """Test that shelf command is simple without PROJECT_ROOT injection."""
        create_production_usersetup(tmp_path)
        usersetup_file = tmp_path / "userSetup.py"
        content = usersetup_file.read_text(encoding="utf-8")
        # The shelf command should directly import and call main()
        assert "maya_outliner.main()" in content
        # Should not have complex sys.path manipulation in command
        assert 'sys.path.insert' not in content.split('command=')[1].split('sourceType')[0]

    def test_usersetup_is_valid_python(self, tmp_path: Path) -> None:
        """Test that generated userSetup.py is valid Python syntax."""
        create_production_usersetup(tmp_path)
        usersetup_file = tmp_path / "userSetup.py"
        content = usersetup_file.read_text(encoding="utf-8")
        # This will raise SyntaxError if invalid
        compile(content, usersetup_file, "exec")


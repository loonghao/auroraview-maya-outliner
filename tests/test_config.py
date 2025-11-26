"""Tests for environment configuration auto-detection.

These tests directly import the config module to avoid the maya_outliner import chain
that requires external dependencies (auroraview, maya).
"""

import importlib.util
import os
from pathlib import Path
from unittest.mock import patch



def _load_config_module():
    """Load config module directly without going through __init__.py."""
    config_path = Path(__file__).parent.parent / "auroraview_maya_outliner" / "config.py"
    spec = importlib.util.spec_from_file_location("config", config_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


config_module = _load_config_module()


class TestEnvironmentConfig:
    """Test EnvironmentConfig class."""

    def _create_config(self, tmp_path: Path) -> config_module.EnvironmentConfig:
        """Create a config instance with mocked paths."""
        config = object.__new__(config_module.EnvironmentConfig)
        config._project_root = tmp_path
        config._dist_dir = tmp_path / "dist"
        config._index_html = tmp_path / "dist" / "index.html"
        return config

    def test_is_production_when_env_set_to_production(self, tmp_path: Path) -> None:
        """Test is_production returns True when AURORAVIEW_ENV is 'production'."""
        config = self._create_config(tmp_path)

        with patch.dict(os.environ, {"AURORAVIEW_ENV": "production"}):
            assert config.is_production is True
            assert config.is_development is False

    def test_is_production_when_env_set_to_prod(self, tmp_path: Path) -> None:
        """Test is_production returns True when AURORAVIEW_ENV is 'prod'."""
        config = self._create_config(tmp_path)

        with patch.dict(os.environ, {"AURORAVIEW_ENV": "prod"}):
            assert config.is_production is True
            assert config.is_development is False

    def test_is_development_when_env_set_to_development(self, tmp_path: Path) -> None:
        """Test is_development returns True when AURORAVIEW_ENV is 'development'."""
        config = self._create_config(tmp_path)

        with patch.dict(os.environ, {"AURORAVIEW_ENV": "development"}):
            assert config.is_development is True
            assert config.is_production is False

    def test_is_development_when_env_set_to_dev(self, tmp_path: Path) -> None:
        """Test is_development returns True when AURORAVIEW_ENV is 'dev'."""
        config = self._create_config(tmp_path)

        with patch.dict(os.environ, {"AURORAVIEW_ENV": "dev"}):
            assert config.is_development is True
            assert config.is_production is False

    def test_auto_detect_production_when_dist_exists(self, tmp_path: Path) -> None:
        """Test auto-detection uses production mode when dist exists."""
        # Create dist directory with index.html
        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()
        (dist_dir / "index.html").write_text("<html></html>")

        config = self._create_config(tmp_path)

        # Clear environment variable to trigger auto-detection
        env = os.environ.copy()
        env.pop("AURORAVIEW_ENV", None)
        with patch.dict(os.environ, env, clear=True):
            assert config.dist_exists is True
            assert config.is_production is True
            assert config.is_development is False

    def test_auto_detect_development_when_dist_not_exists(self, tmp_path: Path) -> None:
        """Test auto-detection uses development mode when dist doesn't exist."""
        config = self._create_config(tmp_path)

        # Clear environment variable to trigger auto-detection
        env = os.environ.copy()
        env.pop("AURORAVIEW_ENV", None)
        with patch.dict(os.environ, env, clear=True):
            assert config.dist_exists is False
            assert config.is_development is True
            assert config.is_production is False

    def test_get_static_url_returns_file_url(self, tmp_path: Path) -> None:
        """Test get_static_url returns proper file:// URL."""
        # Create dist directory with index.html
        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()
        index_html = dist_dir / "index.html"
        index_html.write_text("<html></html>")

        config = self._create_config(tmp_path)

        url = config.get_static_url()
        assert url is not None
        assert url.startswith("file:///")
        assert "index.html" in url

    def test_get_static_url_returns_none_when_no_dist(self, tmp_path: Path) -> None:
        """Test get_static_url returns None when dist doesn't exist."""
        config = self._create_config(tmp_path)

        url = config.get_static_url()
        assert url is None


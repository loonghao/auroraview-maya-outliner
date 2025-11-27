"""
Environment configuration for AuroraView Maya Outliner

This module handles environment-based configuration for loading frontend resources.
It supports both development (Vite dev server) and production (static files) modes.

Environment Variables:
    AURORAVIEW_ENV: Controls the environment mode
        - "development" or "dev": Use Vite dev server
        - "production" or "prod": Use static built files from dist/
        - Not set: Auto-detect based on dist/ existence
            - If dist/index.html exists -> production mode
            - Otherwise -> development mode

Usage:
    from auroraview_maya_outliner.config import get_frontend_url

    # Auto-detect based on environment variable or dist existence
    url = get_frontend_url()

    # Or explicitly specify
    url = get_frontend_url(force_production=True)
"""

import os
from pathlib import Path
from typing import Optional


class EnvironmentConfig:
    """Environment configuration manager for AuroraView Maya Outliner"""

    # Environment variable name
    ENV_VAR = "AURORAVIEW_ENV"

    # Default URLs
    DEV_SERVER_URL = "http://localhost:5173"
    DEV_SERVER_PORT = 5173

    # Valid environment values
    PRODUCTION_VALUES = {"production", "prod"}
    DEVELOPMENT_VALUES = {"development", "dev"}

    def __init__(self):
        """Initialize configuration"""
        self._project_root = Path(__file__).parent.parent
        self._dist_dir = self._project_root / "dist"
        self._index_html = self._dist_dir / "index.html"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode

        Returns:
            True if AURORAVIEW_ENV is set to production/prod,
            or if not set and dist files exist (auto-detection)
        """
        env = os.getenv(self.ENV_VAR, "").lower()
        if env:
            # Explicit environment variable set
            return env in self.PRODUCTION_VALUES
        # Auto-detect: use production if dist exists
        return self.dist_exists

    @property
    def is_development(self) -> bool:
        """Check if running in development mode

        Returns:
            True if AURORAVIEW_ENV is set to development/dev,
            or if not set and dist files don't exist (auto-detection)
        """
        env = os.getenv(self.ENV_VAR, "").lower()
        if env:
            # Explicit environment variable set
            return env in self.DEVELOPMENT_VALUES
        # Auto-detect: use development if dist doesn't exist
        return not self.dist_exists

    @property
    def dist_exists(self) -> bool:
        """Check if dist directory and index.html exist

        Returns:
            True if dist/index.html exists
        """
        return self._index_html.exists()

    def get_static_url(self) -> Optional[str]:
        """Get file:// URL for static built files

        Returns:
            file:// URL if dist/index.html exists, None otherwise
        """
        if not self.dist_exists:
            return None

        # Convert to absolute path and use forward slashes
        abs_path = self._index_html.resolve()
        # Windows: C:/path/to/file -> file:///C:/path/to/file
        return f"file:///{abs_path.as_posix()}"

    def get_dist_dir(self) -> Optional[Path]:
        """Get the dist directory path for asset_root

        Returns:
            Path to dist directory if it exists, None otherwise
        """
        if not self.dist_exists:
            return None
        return self._dist_dir.resolve()

    def get_index_html_path(self) -> Optional[Path]:
        """Get the index.html file path

        Returns:
            Path to index.html if it exists, None otherwise
        """
        if not self.dist_exists:
            return None
        return self._index_html.resolve()

    def get_dev_url(self) -> str:
        """Get development server URL

        Returns:
            Development server URL (http://localhost:5173)
        """
        return self.DEV_SERVER_URL

    def get_url(self, force_production: bool = False, force_development: bool = False) -> str:
        """Get frontend URL based on environment configuration

        Args:
            force_production: Force production mode regardless of environment variable
            force_development: Force development mode regardless of environment variable

        Returns:
            Frontend URL (either file:// for production or http:// for development)

        Raises:
            FileNotFoundError: If production mode is requested but dist files don't exist
        """
        # Handle force flags
        if force_production and force_development:
            raise ValueError("Cannot force both production and development mode")

        # Determine mode
        use_production = force_production or (not force_development and self.is_production)

        if use_production:
            # Production mode: use static files
            static_url = self.get_static_url()
            if static_url is None:
                raise FileNotFoundError(
                    f"Production mode requested but dist files not found.\n"
                    f"Expected: {self._index_html}\n"
                    f"Please run: npm run build"
                )
            return static_url
        else:
            # Development mode: use dev server
            return self.get_dev_url()

    def get_environment_info(self) -> dict:
        """Get environment configuration information

        Returns:
            Dictionary with environment configuration details
        """
        return {
            "env_var": self.ENV_VAR,
            "env_value": os.getenv(self.ENV_VAR, "<not set>"),
            "is_production": self.is_production,
            "is_development": self.is_development,
            "dist_exists": self.dist_exists,
            "dist_path": str(self._dist_dir),
            "index_html_path": str(self._index_html),
            "dev_server_url": self.DEV_SERVER_URL,
            "current_url": self.get_url() if self.is_development or self.dist_exists else "<unavailable>",
        }


# Global instance - use this directly or via convenience functions
_config = EnvironmentConfig()

# Convenience functions - delegate to global instance
get_frontend_url = _config.get_url
get_environment_info = _config.get_environment_info
get_dist_dir = _config.get_dist_dir
get_index_html_path = _config.get_index_html_path


def is_production() -> bool:
    """Check if running in production mode"""
    return _config.is_production


__all__ = [
    "get_frontend_url",
    "get_environment_info",
    "get_dist_dir",
    "get_index_html_path",
    "is_production",
    "EnvironmentConfig",
]


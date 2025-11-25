"""
Example usage of AuroraView Maya Outliner with environment configuration

This script demonstrates different ways to launch the Maya Outliner
with development and production modes.
"""

import os


def example_auto_detect():
    """Example 1: Auto-detect mode based on AURORAVIEW_ENV environment variable"""
    print("=" * 60)
    print("Example 1: Auto-detect mode")
    print("=" * 60)

    from maya_integration import main
    from maya_integration.config import get_environment_info

    # Print current environment info
    info = get_environment_info()
    print(f"\nEnvironment Variable: {info['env_value']}")
    print(f"Mode: {'Production' if info['is_production'] else 'Development'}")
    print(f"URL: {info['current_url']}")
    print(f"Dist exists: {info['dist_exists']}\n")

    # Launch outliner (auto-detects mode)
    main()


def example_force_production():
    """Example 2: Force production mode (use static files)"""
    print("=" * 60)
    print("Example 2: Force production mode")
    print("=" * 60)

    from maya_integration import MayaOutliner

    # Create outliner instance
    outliner = MayaOutliner()

    # Force production mode
    print("\nForcing production mode (static files)...")
    outliner.run(use_local=True)


def example_force_development():
    """Example 3: Force development mode (use dev server)"""
    print("=" * 60)
    print("Example 3: Force development mode")
    print("=" * 60)

    from maya_integration import MayaOutliner

    # Set environment to development
    os.environ['AURORAVIEW_ENV'] = 'development'

    # Create outliner instance
    outliner = MayaOutliner()

    # Run with auto-detect (will use development mode)
    print("\nForcing development mode (dev server)...")
    outliner.run()


def example_custom_url():
    """Example 4: Use custom URL"""
    print("=" * 60)
    print("Example 4: Custom URL")
    print("=" * 60)

    from maya_integration import MayaOutliner

    # Create outliner instance
    outliner = MayaOutliner()

    # Use custom URL
    custom_url = "http://localhost:8080"
    print(f"\nUsing custom URL: {custom_url}...")
    outliner.run(url=custom_url)


def example_check_config():
    """Example 5: Check current configuration"""
    print("=" * 60)
    print("Example 5: Check configuration")
    print("=" * 60)

    from maya_integration.config import get_environment_info

    info = get_environment_info()

    print("\nCurrent Configuration:")
    print("-" * 40)
    print(f"Environment Variable: {info['env_var']}")
    print(f"Environment Value: {info['env_value']}")
    print(f"Is Production: {info['is_production']}")
    print(f"Is Development: {info['is_development']}")
    print(f"Dist Exists: {info['dist_exists']}")
    print(f"Dist Path: {info['dist_path']}")
    print(f"Index HTML Path: {info['index_html_path']}")
    print(f"Dev Server URL: {info['dev_server_url']}")
    print(f"Current URL: {info['current_url']}")
    print("-" * 40)


def example_switch_modes():
    """Example 6: Switch between modes"""
    print("=" * 60)
    print("Example 6: Switch between modes")
    print("=" * 60)

    from maya_integration.config import get_environment_info

    # Check current mode
    info = get_environment_info()
    print(f"\nCurrent mode: {'Production' if info['is_production'] else 'Development'}")

    # Switch to production
    print("\nSwitching to production mode...")
    os.environ['AURORAVIEW_ENV'] = 'production'
    info = get_environment_info()
    print(f"New mode: {'Production' if info['is_production'] else 'Development'}")
    print(f"URL: {info['current_url']}")

    # Switch to development
    print("\nSwitching to development mode...")
    os.environ['AURORAVIEW_ENV'] = 'development'
    info = get_environment_info()
    print(f"New mode: {'Production' if info['is_production'] else 'Development'}")
    print(f"URL: {info['current_url']}")


if __name__ == "__main__":
    # Run examples (comment out the ones you don't want to run)

    # Example 1: Auto-detect mode
    # example_auto_detect()

    # Example 2: Force production mode
    # example_force_production()

    # Example 3: Force development mode
    # example_force_development()

    # Example 4: Custom URL
    # example_custom_url()

    # Example 5: Check configuration
    example_check_config()

    # Example 6: Switch between modes
    # example_switch_modes()


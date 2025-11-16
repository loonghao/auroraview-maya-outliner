"""Test script to verify AuroraView API update

This script tests the updated maya_outliner.py with the latest AuroraView API.

Usage in Maya:
    import sys
    sys.path.insert(0, r"C:\github\auroraview-maya-outliner")
    exec(open(r"C:\github\auroraview-maya-outliner\test_api_update.py").read())
"""

import sys
import traceback

print("=" * 80)
print("AuroraView API Update Test")
print("=" * 80)
print()

# Test 1: Import AuroraView
print("Test 1: Import AuroraView")
print("-" * 80)
try:
    from auroraview import EventTimer, QtWebView, WebView

    print("✓ Successfully imported: EventTimer, QtWebView, WebView")

    # Check WebView.create() method
    if hasattr(WebView, "create"):
        print("✓ WebView.create() method available")
    else:
        print("✗ WebView.create() method NOT available")

    # Check EventTimer features
    timer_attrs = ["start", "stop", "cleanup", "on_close", "on_tick"]
    missing_attrs = [attr for attr in timer_attrs if not hasattr(EventTimer, attr)]
    if not missing_attrs:
        print(f"✓ EventTimer has all expected methods: {', '.join(timer_attrs)}")
    else:
        print(f"✗ EventTimer missing methods: {', '.join(missing_attrs)}")

except ImportError as e:
    print(f"✗ Failed to import AuroraView: {e}")
    traceback.print_exc()
    sys.exit(1)

print()

# Test 2: Import maya_outliner
print("Test 2: Import maya_outliner")
print("-" * 80)
try:
    from maya_integration import maya_outliner

    print("✓ Successfully imported maya_outliner")

    # Check MayaOutliner class
    if hasattr(maya_outliner, "MayaOutliner"):
        print("✓ MayaOutliner class available")

        # Check __init__ signature
        import inspect

        sig = inspect.signature(maya_outliner.MayaOutliner.__init__)
        params = list(sig.parameters.keys())
        print(f"  __init__ parameters: {params}")

        if "use_qt" in params:
            print("  ✓ use_qt parameter available")
        else:
            print("  ✗ use_qt parameter NOT available")

    # Check main() function signature
    if hasattr(maya_outliner, "main"):
        print("✓ main() function available")

        sig = inspect.signature(maya_outliner.main)
        params = list(sig.parameters.keys())
        print(f"  main() parameters: {params}")

        expected_params = ["url", "use_local", "singleton", "use_qt"]
        missing_params = [p for p in expected_params if p not in params]
        if not missing_params:
            print(f"  ✓ All expected parameters available: {', '.join(expected_params)}")
        else:
            print(f"  ✗ Missing parameters: {', '.join(missing_params)}")

except ImportError as e:
    print(f"✗ Failed to import maya_outliner: {e}")
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: Check for removed methods
print("Test 3: Check for removed/updated methods")
print("-" * 80)
try:
    outliner_class = maya_outliner.MayaOutliner

    # These methods should be removed or updated
    removed_methods = ["_start_event_processing", "_stop_event_processing"]
    updated_methods = ["_get_event_timer"]

    for method in removed_methods:
        if hasattr(outliner_class, method):
            print(f"  ⚠ Old method still exists: {method}")
        else:
            print(f"  ✓ Old method removed: {method}")

    for method in updated_methods:
        if hasattr(outliner_class, method):
            print(f"  ✓ Updated method exists: {method}")
        else:
            print(f"  ✗ Updated method missing: {method}")

except Exception as e:
    print(f"✗ Error checking methods: {e}")
    traceback.print_exc()

print()

# Test 4: Test WebView.create() API
print("Test 4: Test WebView.create() API")
print("-" * 80)
try:
    # Check create() signature
    sig = inspect.signature(WebView.create)
    params = list(sig.parameters.keys())
    print(f"WebView.create() parameters: {params}")

    # Check for new parameters
    new_params = ["auto_show", "auto_timer", "singleton", "mode", "debug"]
    missing_params = [p for p in new_params if p not in params]
    if not missing_params:
        print(f"✓ All new parameters available: {', '.join(new_params)}")
    else:
        print(f"✗ Missing parameters: {', '.join(missing_params)}")

except Exception as e:
    print(f"✗ Error checking WebView.create(): {e}")
    traceback.print_exc()

print()
print("=" * 80)
print("✓ API Update Test Complete!")
print("=" * 80)
print()
print("Next steps:")
print("  1. Test in Maya: just maya-2024-local")
print("  2. Click the 'Outliner' button on the AuroraView shelf")
print("  3. Verify the outliner window opens correctly")
print("  4. Check the Script Editor for any errors")
print()


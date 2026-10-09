"""Verify fixed public GUI imports in mayapy without creating an application."""

import argparse
import hashlib
import importlib.metadata
import json
import sys
import zipfile
from pathlib import Path

if __package__:
    from .contract_runtime import inside, verify_runtime
else:
    from contract_runtime import inside, verify_runtime


NATIVE_SHA = "e30ac11fad4acd7f24aa29e8599be9fb4c99ea7a92211909b8e379be4dd72ab7"


def verify_native(runtime, wheel):
    runtime, wheel = Path(runtime).resolve(), Path(wheel).resolve()
    if hashlib.sha256(wheel.read_bytes()).hexdigest() != NATIVE_SHA:
        raise ValueError("Public AuroraView 0.5.12 wheel SHA256 mismatch")
    checked = 0
    with zipfile.ZipFile(wheel) as archive:
        for entry in archive.infolist():
            if entry.is_dir() or not entry.filename.startswith("auroraview/"):
                continue
            destination = runtime / entry.filename
            if not inside(destination, runtime):
                raise ValueError("Wheel path escaped runtime")
            if destination.read_bytes() != archive.read(entry):
                raise ValueError("Installed public wheel differs: " + entry.filename)
            checked += 1
    if not checked:
        raise ValueError("Wheel contains no AuroraView runtime")
    return checked


def check(runtime, wheel, contract_runtime):
    runtime, contract_runtime = Path(runtime).resolve(), Path(contract_runtime).resolve()
    checked = verify_native(runtime, wheel)
    contract = verify_runtime(contract_runtime)
    sys.path[:0] = [str(runtime), str(contract_runtime)]
    import auroraview
    import auroraview_dcc_mcp
    import dcc_mcp_core
    import qtpy
    from auroraview import QtWebView
    from qtpy.QtWidgets import QApplication

    assert QApplication.instance() is None, "Import probe must not start a GUI"
    assert qtpy.API_NAME == "PySide6", qtpy.API_NAME
    imports = {
        "auroraview": auroraview.__file__, "qtpy": qtpy.__file__,
        "contract": auroraview_dcc_mcp.__file__, "core": dcc_mcp_core.__file__,
    }
    for key in ("auroraview", "qtpy"):
        assert inside(imports[key], runtime), imports[key]
    for key in ("contract", "core"):
        assert inside(imports[key], contract_runtime), imports[key]
    expected = {
        "auroraview": "0.5.12", "QtPy": "2.4.3", "packaging": "25.0",
        "auroraview-dcc-mcp": "0.1.0", "dcc-mcp-core": "0.20.41",
    }
    versions = {name: importlib.metadata.version(name) for name in expected}
    assert versions == expected, versions
    methods = ("bind_call", "bind_api", "load_file", "eval_js", "on", "destroy", "get_hwnd")
    assert all(callable(getattr(QtWebView, name, None)) for name in methods)
    return {
        "status": "passed", "level": "mayapy-public-gui-imports",
        "versions": versions, "qt_binding": qtpy.API_NAME, "python": sys.version,
        "native_wheel_sha256": NATIVE_SHA, "verified_runtime_files": checked,
        "contract": contract, "imports": imports, "qtwebview_methods": list(methods),
        "application_created": False, "interactive_webview": "not-tested", "docking": "not-tested",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("runtime", "wheel", "contract_runtime", "report"):
        parser.add_argument(name)
    args = parser.parse_args()
    result = check(args.runtime, args.wheel, args.contract_runtime)
    report = Path(args.report).resolve()
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

"""Keep local native builds out of the fixed public GUI acceptance gate."""

import hashlib
import zipfile

import pytest

from scripts import check_maya_gui_runtime


def wheel(tmp_path, name, data, monkeypatch):
    path = tmp_path / "public.whl"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(name, data)
    monkeypatch.setattr(check_maya_gui_runtime, "NATIVE_SHA", hashlib.sha256(path.read_bytes()).hexdigest())
    return path


def test_native_gate_refuses_wrong_public_checksum(tmp_path):
    path = tmp_path / "native.whl"
    path.write_bytes(b"unverified build")
    with pytest.raises(ValueError, match="SHA256"):
        check_maya_gui_runtime.verify_native(tmp_path / "runtime", path)


def test_native_gate_compares_installed_module_bytes_to_verified_wheel(tmp_path, monkeypatch):
    path = wheel(tmp_path, "auroraview/_core.pyd", b"public", monkeypatch)
    runtime = tmp_path / "runtime"
    (runtime / "auroraview").mkdir(parents=True)
    installed = runtime / "auroraview" / "_core.pyd"
    installed.write_bytes(b"local build")
    with pytest.raises(ValueError, match="differs"):
        check_maya_gui_runtime.verify_native(runtime, path)
    installed.write_bytes(b"public")
    assert check_maya_gui_runtime.verify_native(runtime, path) == 1


def test_native_gate_refuses_paths_outside_runtime(tmp_path, monkeypatch):
    path = wheel(tmp_path, "auroraview/../../outside", b"public", monkeypatch)
    with pytest.raises(ValueError, match="escaped"):
        check_maya_gui_runtime.verify_native(tmp_path / "runtime", path)

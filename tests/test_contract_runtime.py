"""Artifact and launch checks do not start Maya or install packages."""

import hashlib
import io
import json
from unittest.mock import Mock

import pytest

from scripts import prepare_maya_contract, run_maya_contract
from scripts.contract_runtime import CORE_VERSION, RECEIPT, inside, verify_runtime, wheel_name
from scripts.maya_contract_acceptance import result_value
from scripts import maya_contract_acceptance

URL = "https://github.com/try-auroraview/auroraview/releases/download/preview/auroraview_dcc_mcp-0.1.0-py3-none-any.whl"
DATA = b"verified wheel bytes"
SHA = hashlib.sha256(DATA).hexdigest()


def runtime_receipt(path):
    artifact = path / ".artifacts" / wheel_name(URL, SHA)
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(DATA)
    receipt = {"wheel_url": URL, "wheel_sha256": SHA, "core_version": CORE_VERSION}
    (path / RECEIPT).write_text(json.dumps(receipt), encoding="utf-8")
    return receipt


@pytest.mark.parametrize("url,sha", [(URL.replace("https:", "http:"), SHA), (URL, "bad"), (URL.replace(".whl", ".zip"), SHA)])
def test_runtime_requires_https_wheel_and_exact_checksum(url, sha):
    with pytest.raises(ValueError):
        wheel_name(url, sha)


def test_runtime_detects_modified_artifact_and_wrong_core(tmp_path):
    receipt = runtime_receipt(tmp_path)
    assert verify_runtime(tmp_path) == receipt
    artifact = tmp_path / ".artifacts" / wheel_name(URL, SHA)
    artifact.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="SHA256"):
        verify_runtime(tmp_path)
    artifact.write_bytes(DATA)
    receipt["core_version"] = "0.20.25"
    (tmp_path / RECEIPT).write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(ValueError, match="0.20.41"):
        verify_runtime(tmp_path)


def test_failed_download_hash_never_installs_runtime(tmp_path, monkeypatch):
    mayapy = tmp_path / "mayapy.exe"
    mayapy.touch()
    monkeypatch.setattr(prepare_maya_contract, "urlopen", lambda *_args, **_kwargs: io.BytesIO(b"wrong"))
    install = Mock()
    monkeypatch.setattr(prepare_maya_contract.subprocess, "run", install)
    with pytest.raises(ValueError, match="SHA256"):
        prepare_maya_contract.prepare(mayapy, tmp_path / "runtime", URL, SHA)
    install.assert_not_called()


def test_public_artifact_is_verified_before_pinned_install(tmp_path, monkeypatch):
    mayapy, target = tmp_path / "mayapy.exe", tmp_path / "runtime"
    mayapy.touch()
    monkeypatch.setattr(prepare_maya_contract, "urlopen", lambda *_args, **_kwargs: io.BytesIO(DATA))
    install = Mock()
    monkeypatch.setattr(prepare_maya_contract.subprocess, "run", install)
    prepare_maya_contract.prepare(mayapy, target, URL, SHA)
    args = install.call_args.args[0]
    assert args[:4] == ["vx", "uv", "pip", "install"]
    assert args[-1] == "dcc-mcp-core==0.20.41"
    assert args[-2].endswith(".whl[core]")
    assert verify_runtime(target)["wheel_sha256"] == SHA


def test_launcher_isolates_startup_and_preserves_mayapy_exit(tmp_path, monkeypatch):
    mayapy, runtime = tmp_path / "mayapy.exe", tmp_path / "runtime"
    mayapy.touch()
    runtime_receipt(runtime)
    monkeypatch.setenv("PYTHONPATH", "unrelated-source-tree")
    launch = Mock(return_value=7)
    monkeypatch.setattr(run_maya_contract.subprocess, "call", launch)
    assert run_maya_contract.launch(mayapy, runtime, tmp_path / "result.json") == 7
    environment = launch.call_args.kwargs["env"]
    assert "PYTHONPATH" not in environment
    assert environment["MAYA_SKIP_USERSETUP_PY"] == "1"
    assert environment["PYTHONNOUSERSITE"] == "1"
    assert "maya_contract_acceptance.py" in launch.call_args.args[0][1]


def test_import_path_check_does_not_accept_a_similar_sibling(tmp_path):
    assert inside(tmp_path / "runtime" / "module.py", tmp_path / "runtime")
    assert not inside(tmp_path / "runtime-other" / "module.py", tmp_path / "runtime")


@pytest.mark.parametrize("response", [{"error": {"code": -1}}, {"result": {"isError": True}}])
def test_mcp_error_envelope_is_never_accepted_as_success(response):
    with pytest.raises(AssertionError):
        result_value(response)


def test_tool_discovery_consumes_all_pages(monkeypatch):
    pages = Mock(side_effect=[
        {"result": {"tools": [{"name": "first"}], "nextCursor": "next"}},
        {"result": {"tools": [{"name": "last"}]}},
    ])
    monkeypatch.setattr(maya_contract_acceptance, "rpc", pages)
    receipts = []
    assert maya_contract_acceptance.list_tools("url", "pump", receipts) == [{"name": "first"}, {"name": "last"}]
    assert pages.call_args.args[-1] == {"cursor": "next"}
    assert receipts == [{"tool_count": 1, "has_next_page": True}, {"tool_count": 1, "has_next_page": False}]


def test_failed_gate_preserves_json_receipt(tmp_path, monkeypatch):
    report = tmp_path / "failed.json"
    monkeypatch.setattr(maya_contract_acceptance.sys, "argv", ["gate", "--runtime", "runtime", "--report", str(report)])
    monkeypatch.setattr(maya_contract_acceptance, "run_gate", Mock(side_effect=RuntimeError("host failed")))
    with pytest.raises(RuntimeError, match="host failed"):
        maya_contract_acceptance.main()
    receipt = json.loads(report.read_text(encoding="utf-8"))
    assert receipt["status"] == "failed"
    assert "host failed" in receipt["traceback"]

"""Public artifact receipt checks shared by preparation and Maya acceptance."""

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

CORE_VERSION = "0.20.41"
RECEIPT = "contract-runtime.json"


def wheel_name(url, sha256):
    parsed = urlparse(url)
    name = Path(unquote(parsed.path)).name
    if parsed.scheme != "https" or not parsed.netloc or not name.endswith(".whl"):
        raise ValueError("Supply a public HTTPS wheel URL")
    if not name.startswith("auroraview_dcc_mcp-"):
        raise ValueError("Expected an auroraview-dcc-mcp wheel")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", sha256):
        raise ValueError("Supply the release's 64-character SHA256")
    return name


def verify_wheel(path, sha256):
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest != sha256.lower():
        raise ValueError("Public wheel SHA256 mismatch")
    return digest


def verify_runtime(runtime):
    runtime = Path(runtime).resolve()
    receipt = json.loads((runtime / RECEIPT).read_text(encoding="utf-8"))
    name = wheel_name(receipt["wheel_url"], receipt["wheel_sha256"])
    if receipt["core_version"] != CORE_VERSION:
        raise ValueError("Acceptance requires dcc-mcp-core==" + CORE_VERSION)
    verify_wheel(runtime / ".artifacts" / name, receipt["wheel_sha256"])
    return receipt


def inside(path, directory):
    try:
        Path(path).resolve().relative_to(Path(directory).resolve())
    except ValueError:
        return False
    return True

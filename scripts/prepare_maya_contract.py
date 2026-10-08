"""Download a public wheel, verify it, and install an isolated Maya runtime."""

import argparse
import json
import subprocess
from pathlib import Path
from urllib.request import urlopen

if __package__:
    from .contract_runtime import CORE_VERSION, RECEIPT, verify_wheel, wheel_name
else:
    from contract_runtime import CORE_VERSION, RECEIPT, verify_wheel, wheel_name


def prepare(mayapy, target, url, sha256):
    mayapy, target = Path(mayapy).resolve(), Path(target).resolve()
    if not mayapy.is_file():
        raise ValueError("Maya interpreter does not exist: " + str(mayapy))
    name = wheel_name(url, sha256)
    if target.exists() and any(target.iterdir()):
        raise ValueError("Use an empty isolated runtime directory")
    artifacts = target / ".artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    wheel = artifacts / name
    with urlopen(url, timeout=60) as response:
        wheel.write_bytes(response.read())
    digest = verify_wheel(wheel, sha256)
    subprocess.run(
        ["vx", "uv", "pip", "install", "--python", str(mayapy), "--target", str(target),
         str(wheel) + "[core]", "dcc-mcp-core==" + CORE_VERSION],
        check=True,
    )
    receipt = {"wheel_url": url, "wheel_sha256": digest, "core_version": CORE_VERSION}
    (target / RECEIPT).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mayapy")
    parser.add_argument("target")
    parser.add_argument("wheel_url")
    parser.add_argument("sha256")
    args = parser.parse_args()
    print(json.dumps(prepare(args.mayapy, args.target, args.wheel_url, args.sha256), indent=2))


if __name__ == "__main__":
    main()

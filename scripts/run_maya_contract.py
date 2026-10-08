"""Launch only the standalone consumer gate with an explicit public runtime."""

import argparse
import os
import subprocess
from pathlib import Path

if __package__:
    from .contract_runtime import verify_runtime
else:
    from contract_runtime import verify_runtime


def launch(mayapy, runtime, report):
    mayapy, runtime = Path(mayapy).resolve(), Path(runtime).resolve()
    if not mayapy.is_file():
        raise ValueError("Maya interpreter does not exist: " + str(mayapy))
    verify_runtime(runtime)
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment["PYTHONNOUSERSITE"] = "1"
    environment["MAYA_SKIP_USERSETUP_PY"] = "1"
    script = Path(__file__).with_name("maya_contract_acceptance.py").resolve()
    return subprocess.call(
        [str(mayapy), str(script), "--runtime", str(runtime), "--report", str(Path(report).resolve())],
        env=environment,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mayapy")
    parser.add_argument("runtime")
    parser.add_argument("report")
    args = parser.parse_args()
    raise SystemExit(launch(args.mayapy, args.runtime, args.report))


if __name__ == "__main__":
    main()

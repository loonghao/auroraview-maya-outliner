"""Invoke the supplied Maya interpreter, preserving its exit code."""

import os
import subprocess
import sys
from pathlib import Path

mayapy = Path(sys.argv[1])
if not mayapy.is_file():
    raise SystemExit("Maya interpreter does not exist: {}".format(mayapy))
script = Path(__file__).with_name("maya_smoke.py").resolve()
environment = os.environ.copy()
# This scene-only gate must not execute an installed user's startup scripts.
environment["MAYA_SKIP_USERSETUP_PY"] = "1"
raise SystemExit(subprocess.call([str(mayapy), str(script)], env=environment))

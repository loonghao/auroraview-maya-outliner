set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

default:
    @vx just --list

install:
    vx npm ci

dev:
    vx npm run dev -- --host 127.0.0.1

build:
    vx npm run build

test:
    vx uv run --no-project --python 3.11 --with pytest pytest -c pytest.ini tests -q

# Source demo archive; the runtime is installed separately in Maya's Python.
package version="0.1.0-test":
    vx uv run --no-project --python 3.11 build_maya_package.py --version {{version}} --skip-vendor

check: build test

# Native Maya scene test; no window is opened and no user preferences are edited.
maya-smoke mayapy:
    vx uv run --no-project --python 3.11 scripts/run_maya_smoke.py "{{mayapy}}"

# Install into an explicit directory, then add that directory to Maya's sys.path.
maya-runtime mayapy target:
    vx uv pip install --python "{{mayapy}}" --target "{{target}}" auroraview qtpy

verify-package archive="dist/maya-outliner-0.1.0-test.zip":
    vx uv run --no-project --python 3.11 scripts/verify_package.py "{{archive}}"

# Refresh the lockfile within declared compatible dependency ranges.
update:
    vx npm update

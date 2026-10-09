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

# Fixed public GUI candidate; never install another Qt binding into Maya.
maya-gui-runtime mayapy target:
    vx uv pip install --python "{{mayapy}}" --target "{{target}}" --no-deps --no-compile-bytecode --require-hashes --requirements scripts/maya-gui-runtime.txt

maya-gui-imports mayapy runtime wheel contract_runtime report:
    vx uv run --offline --no-project --no-sync -- "{{mayapy}}" -B scripts/check_maya_gui_runtime.py "{{runtime}}" "{{wheel}}" "{{contract_runtime}}" "{{report}}"

# Public wheel only: verify SHA256 before installing into an empty directory.
maya-contract-runtime mayapy target wheel_url sha256:
    vx uv run --no-project --python 3.11 scripts/prepare_maya_contract.py "{{mayapy}}" "{{target}}" "{{wheel_url}}" "{{sha256}}"

maya-contract mayapy runtime report=".build/maya-contract-acceptance.json":
    vx uv run --no-project --python 3.11 scripts/run_maya_contract.py "{{mayapy}}" "{{runtime}}" "{{report}}"

# The supplied wheel may be local during development; this is not a host gate.
test-contracts wheel:
    vx uv run --no-project --python 3.11 --with pytest --with "{{wheel}}" pytest -c pytest.ini tests/test_tools.py -q

verify-package archive="dist/maya-outliner-0.1.0-test.zip":
    vx uv run --no-project --python 3.11 scripts/verify_package.py "{{archive}}"

# Refresh the lockfile within declared compatible dependency ranges.
update:
    vx npm update

# Existing interpreter, with no package resolution or runtime installation.
test-local python:
    vx uv run --offline --no-project --no-sync -- "{{python}}" -B -m pytest -c pytest.ini -p no:cacheprovider tests -q

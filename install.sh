#!/usr/bin/env bash
# Sets up usfscript-py: virtual environment, Python dependencies and Chromium.
set -e
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"

if ! command -v "$PY" >/dev/null 2>&1; then
    echo "python3 was not found. Install Python 3.9 or newer and run this again."
    exit 1
fi

if ! "$PY" -c 'import sys; sys.exit(sys.version_info < (3, 9))'; then
    echo "Python 3.9 or newer is required."
    exit 1
fi

if [ ! -d .venv ]; then
    "$PY" -m venv .venv
fi

. .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e .
python -m playwright install chromium

echo
echo "Done. To use it:"
echo "  source .venv/bin/activate"
echo "  python examples/demo.py"

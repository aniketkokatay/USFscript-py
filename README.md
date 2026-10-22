# usfscript-py

usfscript-py continues [USFscript](https://aniketkokatay.github.io/USFscript/) in Python. It is a module for building screens, buttons, keyboards, images and text labels, and running them as a Desmos graph. You describe the screens in Python, and the module writes the matching expressions into a graph and opens it in Chromium.

Pre-built objects (buttons, a number keyboard, labels, a back button) are available directly. For anything else, `add_exp` lets you add your own blocks, images and output labels as raw LaTeX expressions.

## Requirements

- Python 3.9 or newer
- An internet connection (the base graph is fetched from desmos.com and the graph runs on desmos.com)
- Chromium, which the install step downloads through Playwright

## Install

Clone the repository and run the install script. It creates a virtual environment, installs the dependencies and downloads Chromium.

Linux and macOS:

```
git clone https://github.com/aniketkokatay/usfscript-py.git
cd usfscript-py
bash install.sh
```

Windows:

```
git clone https://github.com/aniketkokatay/usfscript-py.git
cd usfscript-py
install.bat
```

To install by hand instead, or to install straight from GitHub without cloning:

```
pip install git+https://github.com/aniketkokatay/usfscript-py.git
python -m playwright install chromium
```

The package is installed as `usfscript-py` and imported as `usf`.

On Linux, if Chromium fails to start because of missing system libraries, run `python -m playwright install-deps chromium` (this needs sudo).

## Usage

Activate the environment, then run the example:

```
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python examples/demo.py
```

A minimal program:

```python
import usf

s1 = usf.screen("Main")
s1.add_button(label="hello", action=s1.switch("Other"))
s1.compile()

s2 = usf.screen("Other")
s2.back("Main")
s2.compile()

usf.run()
```

Every screen must be compiled with `compile()`, and the last line of the program must be `usf.run()`. Anything added to a screen after `compile()` is not included in the graph.

The full reference for screens, buttons, the keyboard, expressions, images and labels is in [docs/documentation.md](docs/documentation.md). A larger example is in [examples/demo.py](examples/demo.py).

## Saving a graph

The graph opens in a Chromium instance started by the module. To keep it or use browser extensions with it, log in to your Desmos account inside that window, save the graph, and open it later in your own browser.

## Project layout

```
src/usf.py            the module
docs/documentation.md reference
examples/demo.py      example program
install.sh            setup script for Linux and macOS
install.bat           setup script for Windows
pyproject.toml        package metadata and dependencies
```

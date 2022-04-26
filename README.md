# TCG-Player Wrapper

[![PyPI - Python](https://img.shields.io/pypi/pyversions/TCG-Player-Wrapper.svg?logo=PyPI&label=Python&style=flat-square)](https://pypi.python.org/pypi/TCG-Player-Wrapper/)
[![PyPI - Status](https://img.shields.io/pypi/status/TCG-Player-Wrapper.svg?logo=PyPI&label=Status&style=flat-square)](https://pypi.python.org/pypi/TCG-Player-Wrapper/)
[![PyPI - Version](https://img.shields.io/pypi/v/TCG-Player-Wrapper.svg?logo=PyPI&label=Version&style=flat-square)](https://pypi.python.org/pypi/TCG-Player-Wrapper/)
[![PyPI - License](https://img.shields.io/pypi/l/TCG-Player-Wrapper.svg?logo=PyPI&label=License&style=flat-square)](https://opensource.org/licenses/GPL-3.0)

[![Black](https://img.shields.io/badge/Black-Enabled-000000?style=flat-square)](https://github.com/psf/black)
[![Flake8](https://img.shields.io/badge/Flake8-Enabled-informational?style=flat-square)](https://github.com/PyCQA/flake8)
[![Pre-Commit](https://img.shields.io/badge/Pre--Commit-Enabled-informational?logo=pre-commit&style=flat-square)](https://github.com/pre-commit/pre-commit)

[![Github - Contributors](https://img.shields.io/github/contributors/Buried-In-Code/TCG-Player-Wrapper.svg?logo=Github&label=Contributors&style=flat-square)](https://github.com/Buried-In-Code/TCG-Player-Wrapper/graphs/contributors)

[![Github Action - Code Analysis](https://img.shields.io/github/workflow/status/Buried-In-Code/TCG-Player-Wrapper/Code%20Analysis?logo=Github-Actions&label=Code-Analysis&style=flat-square)](https://github.com/Buried-In-Code/TCG-Player-Wrapper/actions/workflows/code-analysis.yaml)
[![Github Action - Testing](https://img.shields.io/github/workflow/status/Buried-In-Code/TCG-Player-Wrapper/Testing?logo=Github-Actions&label=Tests&style=flat-square)](https://github.com/Buried-In-Code/TCG-Player-Wrapper/actions/workflows/testing.yaml)

A [Python](https://www.python.org/) wrapper for the [TCG Player](https://tcgplayer.com) API.

## Installation

### Pip

```bash
$ pip3 install -U --user TCG-Player-Wrapper
```

### Poetry

```bash
$ poetry add TCG-Player-Wrapper
```

## Example Usage

```python
from tcg_player.service import TCGPlayer
from tcg_player.sqlite_cache import SQLiteCache

session = TCGPlayer(client_id="Client ID", client_secret="Client Secret", cache=SQLiteCache())
```

## Socials

[![Social - Discord](https://img.shields.io/badge/Discord-The--DEV--Environment-7289DA?logo=Discord&style=flat-square)](https://discord.gg/nqGMeGg)

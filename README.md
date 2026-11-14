# DirtyGenerator

DirtyGenerator is a collection of Python and web projects for generating adult-themed phrases and related content.

## Project layout

- `src/` — Python source code
- `data/` — Text data used by the generators
- `web/` — HTML, CSS, and JavaScript projects
- `docs/` — Project notes and documentation
- `tests/` — Automated checks

## Run the phrase generator

```bash
python3 src/dirty_bbc.py
```

The phrase collection is stored at `data/200_dirty_phrases.txt`.

## Development setup

Use Python 3. The repository's current generator uses only the Python standard library.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

If you add third-party packages, list them in `requirements.txt` and install with:

```bash
python3 -m pip install -r requirements.txt
```

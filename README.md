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

## Run the stateful story generator

`src/smart_story_engine.py` keeps a story bible (character, location,
wardrobe, makeup, nails, POV, and preferred noun) consistent across all beats.
It uses the existing text files for an offline draft by default:

```bash
python3 src/smart_story_engine.py --beats 5 --seed 7
```

To use an OpenAI-compatible text-generation provider, store its key outside
the repository and enable the writer explicitly:

```bash
export DIRTYGEN_API_KEY='your-key'
python3 src/smart_story_engine.py --writer --api-url 'https://provider.example/v1/chat/completions' --model 'model-id'
```

Use `--json` to return the story bible and each individual beat for a future
SwiftUI client. The engine supports fictional, consenting adult characters
only.

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

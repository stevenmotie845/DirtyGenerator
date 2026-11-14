# dirty_generator.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dirty Generator 2.1
===================

Uncensored first-person degrading phrase engine with tight, punchy, 
non-run-on sentences.
"""

from __future__ import annotations

import argparse
import html
import json
import random
import re
import sys
from pathlib import Path

VERSION = "2.1"
DEFAULT_FILE = "dirty_phrases.txt"

ROLES = [
    "worthless sissy whore",
    "brainless bimbo cumslut",
    "pathetic cumslave",
    "cheap street prostitute",
    "gaping anal slut",
    "desperate gloryhole cumdump",
    "humiliated public whore",
    "stretched asshole slave",
    "gagging deepthroat slut",
    "bukkake cumtoilet",
    "leaking creampie dump",
    "sissy pet",
    "ass-to-mouth slut",
    "triple-penetration cumrag",
    "drooling anal addict",
    "brain-dead cock sleeve",
    "truck-stop cumdump",
    "bimbo breeding whore",
    "sissy anal slut",
    "public-use cumdump",
    "wrecked sissy fuckpet",
    "cum-swapping slut",
    "plugged bimbo hole",
    "cock-drunk street whore",
    "slobbering throat slave",
    "loose anal whore",
    "eager cum sponge",
    "braindead bukkake toy",
    "used-up sissy cuntboy",
    "back-alley anal whore",
]

COCKS = [
    "that massive big black cock",
    "a throbbing huge white cock",
    "an enormous big black cock",
    "a fat veiny big white cock",
    "a monster black dick",
    "a thick white cock",
    "a heavy-hanging black cock",
    "an uncut white cock",
    "a black cock thicker than my wrist",
    "a white cock that slapped my cheek",
    "a sweaty stranger's cock",
    "a hard young white cock",
]

ORAL = [
    "gagged violently on",
    "deepthroated",
    "sucked like a starving whore",
    "choked on",
    "swallowed every drop from",
    "slobbered all over",
    "took down my throat",
    "slurped the head of",
    "got my face fucked by",
    "gagged on the shaft of",
]

FUCK = [
    "got my ass pounded by",
    "rode hard",
    "took in double penetration",
    "got my tight hole stretched by",
    "bent over and drilled by",
    "got railed doggy-style by",
    "was used like a fleshlight by",
    "got reamed out by",
    "got fucked stupid by",
    "took deep in my rear by",
]

SCENES = [
    "at the gloryhole",
    "in the dark alley",
    "on the street corner",
    "in the motel room",
    "behind the dumpster",
    "in the club bathroom",
    "against the brick wall",
    "in the truck-stop stall",
    "on the bare mattress",
    "in the back seat",
]

RESULTS = [
    "until thick cum poured from my ass.",
    "leaving a puddle of jizz on my thighs.",
    "while my face was glazed in bukkake.",
    "until my hole gaped wide and drooled.",
    "with my makeup smeared and throat raw.",
    "as warm cum dripped down my legs.",
    "until my legs shook and gave out.",
    "while crying like a pathetic sissy.",
    "leaving my asshole twitching and sore.",
    "while my mouth dripped with spit.",
]

TEMPLATES = [
    "I {oral} {cock} {scene}, {result}",
    "I {fuck} {cock} {scene}, {result}",
    "As a {role}, I {oral} {cock} {scene}, {result}",
    "I got my face fucked by {cock} {scene}, {result}",
    "I took {cock} in my ass {scene}, {result}",
    "I begged for {cock} {scene}, {result}",
    "I swallowed a massive load after I {oral} {cock} {scene}, {result}",
    "Covered in cum, I {fuck} {cock} {scene}, {result}",
]

CATEGORIES = {
    "bbc_anal": {
        "label": "BBC + anal stretching + dripping",
        "cock": ("black", "bbc"),
        "fuck": ("ass", "anal", "stretch", "hole", "drill"),
    },
    "bwc_oral": {
        "label": "BWC + sucking + deepthroat + gagging",
        "cock": ("white", "bwc"),
        "oral": ("gag", "choke", "throat", "swallow", "suck"),
    },
    "group": {
        "label": "Mixed cocks + DP + bukkake",
        "cock": ("black", "white", "BBC", "BWC"),
        "result": ("bukkake", "cum", "puddle"),
    },
    "sissy_bimbo": {
        "label": "Sissy + bimbo + cumslut",
        "role": ("sissy", "bimbo", "cumslut", "cumslave"),
    },
    "public_whore": {
        "label": "Public + gloryhole + prostitute",
        "scene": ("gloryhole", "alley", "street", "dumpster", "bathroom", "wall"),
    },
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Dirty Generator 2.1</title>
<style>
  body {{ background:#111; color:#eee; font:16px/1.6 Georgia, serif; margin:0; padding:2rem; }}
  h1 {{ font-size:1.4rem; letter-spacing:.1em; text-transform:uppercase; color:#e8557f; }}
  ol {{ max-width:60rem; }}
  li {{ margin-bottom:.9rem; padding-bottom:.9rem; border-bottom:1px solid #2a2a2a; }}
</style>
</head>
<body>
<h1>Dirty Generator {version} &mdash; {count} phrases</h1>
<ol>
{items}
</ol>
</body>
</html>
"""

def _pick(pool, keys=None):
    if keys:
        narrowed = [item for item in pool if any(k.lower() in item.lower() for k in keys)]
        if narrowed:
            return random.choice(narrowed)
    return random.choice(pool)

def polish(text: str) -> str:
    text = re.sub(r"\{[a-z0-9_]+\}", "", text)
    text = " ".join(text.split())
    text = text.replace(" ,", ",").replace(",,", ",").replace(" .", ".")
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    if text and not text.endswith((".", "!", "?")):
        text += "."
    return text

def build_phrase(category: str = "mixed") -> str:
    spec = CATEGORIES.get(category, {})
    role = _pick(ROLES, spec.get("role"))
    template = random.choice(TEMPLATES)
    return polish(template.format(
        role=role,
        cock=_pick(COCKS, spec.get("cock")),
        oral=_pick(ORAL, spec.get("oral")),
        fuck=_pick(FUCK, spec.get("fuck")),
        scene=_pick(SCENES, spec.get("scene")),
        result=_pick(RESULTS, spec.get("result")),
    ))

def generate_batch(count: int, category: str = "mixed") -> list:
    seen, out, tries = set(), [], 0
    guard = max(count * 50, 500)
    pool_keys = [k for k in CATEGORIES if k != "mixed"]
    while len(out) < count and tries < guard:
        tries += 1
        cat = random.choice(pool_keys) if category == "all" else category
        phrase = build_phrase(cat)
        if phrase in seen:
            continue
        seen.add(phrase)
        out.append(phrase)
    return out

def render(phrases, fmt: str) -> str:
    numbered = "\n".join(f"{i}. {p}" for i, p in enumerate(phrases, 1))
    if fmt == "json":
        return json.dumps({"generator": f"Dirty Generator {VERSION}", "count": len(phrases), "phrases": phrases}, indent=2)
    if fmt == "md":
        return f"# Dirty Generator {VERSION}\n\n" + numbered + "\n"
    if fmt == "html":
        items = "\n".join(f"  <li>{html.escape(p)}</li>" for p in phrases)
        return HTML_TEMPLATE.format(version=VERSION, count=len(phrases), items=items)
    return numbered + "\n"

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Dirty Generator 2.1")
    parser.add_argument("-n", "--count", type=int, default=10, help="phrases to generate")
    parser.add_argument("-c", "--category", default="mixed", help="category")
    parser.add_argument("-o", "--out", default=None, help="output file")
    parser.add_argument("-f", "--format", default="txt", choices=["txt", "md", "html", "json"])
    return parser.parse_args(argv)

def main(argv=None):
    args = parse_args(argv)
    phrases = generate_batch(args.count, args.category)
    output = render(phrases, args.format)
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Saved {len(phrases)} phrases to {args.out}.")
    else:
        print(output.rstrip())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
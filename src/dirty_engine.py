#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dirty Sentence Engine (v6.0)
============================
Short, hard, first-person past-tense filth. One clause, one optional tail,
optional second sentence. No run-ons, no unfilled tokens.

Style contract:
    I got face fucked by 8 big black cocks and swallowed every drop.
    I got dp'd by 6 cocks balls deep in my asshole.
    I got on my knees and gaped. I pushed out my dildo and had 2 dicks
    in my butthole at once while I moaned in bliss.

Pools are separate by grammatical role so templates can never mis-marry a
verb to a subject:
    passive_verbs.txt  -> end in "by", always followed by a cock count
    active_verbs.txt   -> take a direct object, always followed by a cock count
    oral_tails.txt     -> optional tail, appended after the object
"""

from __future__ import annotations

import argparse
import html
import json
import random
import re
import sys
from pathlib import Path

VERSION = "6.0"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SETTINGS_FILE = BASE_DIR / "settings.json"

DEFAULT_SETTINGS = {"default_count": 50, "default_intensity": 2,
                    "default_filename": "dirty_sentences.txt"}

# kinds.txt format:  singular|plural|tags
DEFAULT_DATA = {
    "kinds.txt": [
        "big black cock|big black cocks|bbc",
        "huge black dick|huge black dicks|bbc",
        "thick black cock|thick black cocks|bbc",
        "massive BBC|massive BBCs|bbc",
        "fat black dick|fat black dicks|bbc",
        "heavy black shaft|heavy black shafts|bbc",
        "big white cock|big white cocks|bwc",
        "huge white dick|huge white dicks|bwc",
        "thick white cock|thick white cocks|bwc",
        "fat BWC|fat BWCs|bwc",
        "pale uncut dick|pale uncut dicks|bwc",
        "heavy white shaft|heavy white shafts|bwc",
        "mixed black and white cock|mixed black and white cocks|mixed",
        "hard young cock|hard young cocks|mixed",
        "veiny stranger cock|veiny stranger cocks|mixed",
        "sweaty stranger cock|sweaty stranger cocks|mixed",
    ],
    "passive_verbs.txt": [
        "got face fucked by", "got throat fucked by", "got dp'd by",
        "got spit roasted by", "got gangbanged by", "got gang fucked by",
        "got my asshole wrecked by", "got my ass reamed by", "got creampied by",
        "got bred by", "got stretched out by", "got pounded by",
        "got slapped and spat on by", "got my throat stretched by",
        "got used by", "got my holes filled by", "got my mouth used by",
        "got gaped wide by", "got my tits slapped by", "got passed around by",
        "got drilled by", "got my ass eaten by",
    ],
    "active_verbs.txt": [
        "sucked", "deepthroated", "gagged on", "slurped on", "licked",
        "slobbered on", "choked on", "swallowed", "worked my tongue around",
        "mouthed", "gulped down",
    ],
    "riding_verbs.txt": [
        "rode", "bounced on", "backed my ass onto", "squatted on",
        "pushed back onto", "took",
    ],
    "oral_tails.txt": [
        "", "", "", "to the balls", "until spit ran down my chin",
        "one after another", "like a starving whore", "until my jaw locked",
        "with my eyes watering", "and moaned around them",
        "until I had to pull off for air", "with spit dripping off my chin",
    ],
    "seconds.txt": [
        "My makeup ran down my face and I didn't care.",
        "Cum dripped out of me onto the floor.",
        "My asshole was gaping and winking.",
        "Everyone watched and I loved every second.",
        "I was dripping and shaking.",
        "They pulled out and I pushed the cum back out.",
        "I licked my lips and asked for more.",
        "My legs gave out and I just lay there.",
        "I could taste myself on their cocks.",
        "Nobody said a word, they just kept going.",
        "My throat was raw and I still wanted it.",
        "I spat the load back out and grinned.",
    ],
    "scenes.txt": [
        "at the truck stop gloryhole", "in the bathroom stall", "in the alley",
        "on the mattress", "in the parking garage", "at the rest stop",
        "in the changing room", "on the balcony", "in the stairwell",
        "at the house party", "in the taxi", "at the laundromat",
    ],
    "cum.txt": [
        "thick juicy cum", "warm loads", "fat ropes of cum", "a mouthful of cum",
        "sloppy seconds", "hot cum", "every drop", "their whole load",
    ],
}

# Templates. {cocks} is always a count + noun. {scene} is "" or " at/in ...".
PASSIVE = [
    "I {pv} {cocks}{scene} and swallowed every drop.",
    "I {pv} {cocks}{scene} until my throat was raw.",
    "I {pv} {cocks}{scene} balls deep in my asshole.",
    "I {pv} {cocks}{scene} while I moaned in bliss.",
    "I {pv} {cocks}{scene} with my ass in the air.",
    "I {pv} {cocks}{scene} and begged for more.",
    "I {pv} {cocks}{scene} until I gaped.",
    "I {pv} {cocks}{scene} in every hole I have.",
    "I {pv} {cocks}{scene} and took it without a break.",
    "I {pv} {cocks}{scene} until my legs shook.",
    "I {pv} {cocks}{scene} then licked them clean.",
    "I {pv} {cocks}{scene} and drooled all over myself.",
    "I {pv} {cocks}{scene} until my jaw locked.",
    "I {pv} {cocks}{scene} and thanked them with my mouth full.",
    "I {pv} {cocks}{scene} and pushed back for more.",
    "I {pv} {cocks}{scene} while they held my head still.",
    "I {pv} {cocks}{scene} and came up gasping.",
]

ACTIVE = [
    "I {av} {cocks}{tail}{scene}.",
    "I {av} {cocks}{tail} and moaned around them.",
    "I {av} {cocks}{tail} while they held my head.",
    "I {av} {cocks}{tail} and looked up at them.",
    "I {av} {cocks}{tail} with spit running down my chin.",
    "I {av} {cocks}{tail} and swallowed every drop.",
    "I {av} {cocks}{tail} one by one.",
]

RIDING = [
    "I {rv} {cocks}{scene} until it wrecked me.",
    "I {rv} {cocks}{scene} and took it balls deep.",
    "I {rv} {cocks}{scene} with my tits swinging.",
    "I {rv} {cocks}{scene} and worked it deeper.",
    "I {rv} {cocks}{scene} until my legs burned.",
]

SPECIAL = [
    "I got face fucked by {cocks} and enjoyed swallowing {cum}.",
    "I got put upside down and face fucked until spit and makeup ran down my face.",
    "I got dp'd by {cocks} balls deep in my asshole and screamed into the mattress.",
    "I got on my knees and gagged. I pushed out my dildo and had {n2} dicks in my butthole at once while I moaned in bliss.",
    "I licked and sucked every set of balls before they throated me and gagged me one by one.",
    "I got spit on and smacked by dick while taking cock in my pussy and asshole.",
    "I pushed out my plug and took {n2} cocks in my gaping asshole at once.",
    "I got my ass eaten and fingered while {cocks} waited their turn.",
    "I was bent over and passed around until I couldn't count them anymore.",
    "I gargled their balls one by one and begged to be throated.",
    "I got throat fucked by {cocks} until I gagged and spit up on myself.",
    "I held my cheeks open and let {cocks} pick a hole.",
    "I got bred by {cocks} and pushed it all back out after.",
    "I got my asshole stretched by {cocks} and thanked every one.",
]

CATEGORIES = {
    "bbc": {"label": "big black cock", "tag": "bbc"},
    "bwc": {"label": "big white cock", "tag": "bwc"},
    "mixed": {"label": "mixed cock", "tag": "mixed"},
    "group": {"label": "gangbang / dp", "tag": None,
              "passive": ("gang", "dp'd", "spit roasted", "passed", "drilled")},
    "oral": {"label": "sucking / gagging", "tag": None,
             "passive": ("throat", "mouth", "face")},
    "public": {"label": "public", "scene_heavy": True, "tag": None},
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Dirty Sentences</title>
<style>
body{background:#111;color:#eee;font:17px/1.7 Georgia,serif;margin:0;padding:2rem}
h1{font-size:1.1rem;letter-spacing:.14em;text-transform:uppercase;color:#e8557f}
ol{max-width:58rem}li{margin-bottom:.8rem;padding-bottom:.8rem;border-bottom:1px solid #262626}
</style></head><body><h1>Dirty Sentences __V__</h1><ol>
__B__</ol></body></html>
"""


# ---------------------------------------------------------------- helpers
def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def bootstrap() -> None:
    ensure_dirs()
    for name, lines in DEFAULT_DATA.items():
        p = DATA_DIR / name
        if not p.exists():
            p.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load(name: str) -> list:
    ensure_dirs()
    p = DATA_DIR / name
    if not p.exists():
        if name in DEFAULT_DATA:
            p.write_text("\n".join(DEFAULT_DATA[name]) + "\n", encoding="utf-8")
        else:
            return []
    return [l.strip() for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.strip().startswith("#")]


def load_settings() -> dict:
    s = DEFAULT_SETTINGS.copy()
    if SETTINGS_FILE.exists():
        try:
            s.update(json.loads(SETTINGS_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
    return s


def save_settings(s: dict) -> None:
    SETTINGS_FILE.write_text(json.dumps(s, indent=2), encoding="utf-8")


def _article(word: str) -> str:
    return "an" if word[:1].lower() in "aeiou" else "a"


def _kinds(tag=None) -> list:
    rows = []
    for line in load("kinds.txt"):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 3:
            rows.append(parts[:3])
    if tag:
        hits = [r for r in rows if tag in r[2].split(",")]
        if hits:
            return hits
    return rows or [["cock", "cocks", "mixed"]]


def _cocks(n: int, tag=None) -> str:
    singular, plural, _ = random.choice(_kinds(tag))
    return f"{_article(singular)} {singular}" if n == 1 else f"{n} {plural}"


def _scene(chance: float) -> str:
    if random.random() < chance:
        return " " + random.choice(load("scenes.txt"))
    return ""


def _n() -> int:
    return random.choice([1, 2, 2, 3, 3, 4, 4, 5, 6, 7, 8, 10, 12])


def _n2() -> int:
    return random.choice([2, 2, 3, 3, 4])


def polish(text: str) -> str:
    text = " ".join(text.split())
    text = re.sub(r"\s+([,.;])", r"\1", text)
    text = text.replace("..", ".")
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    if text and not text.endswith((".", "!", "?")):
        text += "."
    return text


def _narrow(pool, keys):
    if keys:
        hits = [x for x in pool if any(k in x.lower() for k in keys)]
        if hits:
            return hits
    return pool


# ---------------------------------------------------------------- builder
def build_sentence(category: str = "mixed", intensity: int = 2) -> str:
    spec = CATEGORIES.get(category, {})
    tag = spec.get("tag")
    scene_chance = 0.45 if spec.get("scene_heavy") else 0.22
    if intensity == 1:
        scene_chance *= 0.4
    if intensity == 3:
        scene_chance = min(0.8, scene_chance + 0.25)

    roll = random.random()
    if roll < 0.18:
        tpl = random.choice(SPECIAL)
    elif roll < 0.40:
        tpl = random.choice(RIDING)
    elif roll < 0.68:
        tpl = random.choice(ACTIVE)
    else:
        tpl = random.choice(PASSIVE)

    if "{rv}" in tpl:
        verb = random.choice(load("riding_verbs.txt"))
        n = random.choice([1, 1, 2, 2, 3])
        scene = _scene(scene_chance)
        text = tpl.format(rv=verb, cocks=_cocks(n, tag), scene=scene)
    elif "{pv}" in tpl:
        verb = random.choice(_narrow(load("passive_verbs.txt"), spec.get("passive")))
        scene = _scene(scene_chance)
        text = tpl.format(pv=verb, cocks=_cocks(_n(), tag), scene=scene)
    elif "{av}" in tpl:
        verb = random.choice(load("active_verbs.txt"))
        tail = random.choice(load("oral_tails.txt"))
        scene = _scene(scene_chance)
        text = tpl.format(av=verb, cocks=_cocks(_n(), tag), tail=tail, scene=scene)
    else:
        text = tpl.format(cocks=_cocks(_n(), tag), n2=_n2(),
                          cum=random.choice(load("cum.txt")))

    # a second short sentence, but only sometimes, so nothing turns run-on
    second_chance = {1: 0.0, 2: 0.3, 3: 0.55}.get(intensity, 0.3)
    if "." not in text[:-1] and random.random() < second_chance:
        text = text.rstrip(".") + ". " + random.choice(load("seconds.txt"))

    return polish(text)


def generate(count: int = 50, category: str = "mixed", intensity: int = 2) -> list:
    out, seen, tries = [], set(), 0
    guard = max(count * 50, 400)
    keys = list(CATEGORIES)
    while len(out) < count and tries < guard:
        tries += 1
        cat = random.choice(keys) if category == "all" else category
        s = build_sentence(cat, intensity)
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


# ---------------------------------------------------------------- export
def render(items: list, fmt: str) -> str:
    if fmt == "json":
        return json.dumps({"engine": f"Dirty Sentences {VERSION}", "count": len(items),
                           "sentences": items}, indent=2, ensure_ascii=False)
    if fmt == "md":
        return f"# Dirty Sentences {VERSION}\n\n" + "\n".join(
            f"{i}. {s}" for i, s in enumerate(items, 1)) + "\n"
    if fmt == "html":
        body = "\n".join(f"  <li>{html.escape(s)}</li>" for s in items)
        return HTML_TEMPLATE.replace("__V__", VERSION).replace("__B__", body)
    return "\n".join(f"{i}. {s}" for i, s in enumerate(items, 1)) + "\n"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------- menu
def menu() -> int:
    bootstrap()
    settings = load_settings()
    while True:
        print("\n" + "=" * 54)
        print(f"DIRTY SENTENCE ENGINE (v{VERSION})")
        print("=" * 54)
        print(f"1. Generate {settings['default_count']} sentences")
        print("2. Generate from one category")
        print("3. Settings")
        print("0. Exit")
        print("=" * 54)
        c = input("Select: ").strip()
        if c == "0":
            return 0
        if c == "3":
            raw = input(f"Default count ({settings['default_count']}): ").strip()
            if raw.isdigit() and int(raw) > 0:
                settings["default_count"] = int(raw)
            raw = input(f"Intensity 1-3 ({settings['default_intensity']}): ").strip()
            if raw.isdigit() and int(raw) in (1, 2, 3):
                settings["default_intensity"] = int(raw)
            save_settings(settings)
            print("Saved.")
            continue
        if c in ("1", "2"):
            cat = "mixed"
            if c == "2":
                print("Categories: " + ", ".join(CATEGORIES))
                cat = input("Category: ").strip() or "mixed"
                if cat not in CATEGORIES:
                    cat = "mixed"
            name = input(f"Filename ({settings['default_filename']}): ").strip() \
                or settings["default_filename"]
            if not name.endswith(".txt"):
                name += ".txt"
            items = generate(settings["default_count"], cat, settings["default_intensity"])
            write(DATA_DIR / name, render(items, "txt"))
            print(f"\n{len(items)} sentences -> data/{name}\n")
            print("\n".join(f"{i}. {s}" for i, s in enumerate(items, 1)))
            input("\nPress Enter...")
        else:
            print("Invalid.")


# ---------------------------------------------------------------- cli
def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="dirty_sentences")
    p.add_argument("-n", "--count", type=int, default=None)
    p.add_argument("-c", "--category", default="mixed",
                   choices=list(CATEGORIES) + ["all"])
    p.add_argument("-x", "--intensity", type=int, default=None, choices=[1, 2, 3])
    p.add_argument("-o", "--out", default=None)
    p.add_argument("-f", "--format", default=None, choices=["txt", "md", "html", "json"])
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("-i", "--interactive", action="store_true")
    p.add_argument("--version", action="version", version=f"Dirty Sentences {VERSION}")
    return p.parse_args(argv)


def main(argv=None) -> int:
    a = parse_args(argv)
    bootstrap()
    if a.seed is not None:
        random.seed(a.seed)
    if a.interactive or (a.count is None and a.out is None and sys.stdin.isatty()):
        try:
            return menu()
        except (KeyboardInterrupt, EOFError):
            print("\nClosed.")
            return 0

    s = load_settings()
    intensity = a.intensity or s["default_intensity"]
    fmt = a.format or ("txt" if not a.out else
                       (Path(a.out).suffix.lstrip(".").lower() or "txt"))
    if fmt not in ("txt", "md", "html", "json"):
        fmt = "txt"
    content = render(generate(a.count or s["default_count"], a.category, intensity), fmt)
    if a.out:
        write(Path(a.out), content)
        print(f"Saved -> {a.out} ({fmt})")
    else:
        print(content.rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dirty Generator 2.1: focused, first-person sentence generation.

Each output sentence is assigned one category. ``all`` rotates across the
small category set instead of mixing every topic into every sentence. Data
lists are loaded from ``src/data`` and the repository-level ``data`` folder.
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
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA_DIRS = (HERE / "data", ROOT / "data")
TOKEN = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


# A sentence uses one of these focused lanes. In ``all`` mode one lane is
# selected for each sentence; category ingredients are never all mixed in.
CATEGORIES = {
    "bbc_anal": {
        "label": "BBC and anal",
        "cock": ("black", "bbc", "ebony"),
        "role": ("anal", "ass", "stretch", "gape"),
        "scene": ("motel", "alley", "truck", "rest", "mattress", "bathroom"),
        "result": ("ass", "gape", "leak", "creampie", "thigh", "stretch"),
        "passive": ("ass", "anal", "stretch", "gape", "drill", "ream", "pound"),
        "active": ("gag", "chok", "suck", "swallow", "deepthroat"),
        "toy": ("plug", "dildo", "anal"),
    },
    "bwc_oral": {
        "label": "BWC and oral",
        "cock": ("white", "bwc", "pale"),
        "role": ("throat", "gag", "bimbo", "cockslut"),
        "scene": ("gloryhole", "bathroom", "motel", "party"),
        "result": ("throat", "spit", "chin", "mouth", "gag", "swallow"),
        "passive": ("throat", "face", "mouth", "gag", "deepthroat"),
        "active": ("gag", "chok", "suck", "swallow", "deepthroat", "lick"),
        "toy": ("vibrat", "wand", "dildo"),
    },
    "group": {
        "label": "Group and double penetration",
        "cock": ("mixed", "two", "three", "pair", "line", "train", "group"),
        "role": ("cumdump", "cumslave", "triple", "bukkake", "group"),
        "scene": ("party", "mattress", "house", "balcony", "bathroom"),
        "result": ("bukkake", "face", "mixed", "passed", "line", "puddle"),
        "passive": ("gang", "dp", "tp", "spit roast", "passed", "drill", "filled"),
        "active": ("suck", "gag", "swallow", "lick", "chok"),
        "toy": ("double", "dildo", "plug"),
    },
    "sissy": {
        "label": "Sissy and bimbo",
        "cock": ("black", "white", "thick", "massive", "monster"),
        "role": ("sissy", "bimbo", "cumslut", "cumslave", "fuckpet", "cuntboy"),
        "scene": ("motel", "salon", "party", "bathroom", "bedroom"),
        "result": ("makeup", "collar", "leak", "drool", "humiliat", "wreck"),
        "passive": ("used", "stretched", "pounded", "drilled", "fucked", "bred"),
        "active": ("suck", "gag", "ride", "swallow", "lick"),
        "toy": ("plug", "dildo", "collar", "wand"),
    },
    "public_whore": {
        "label": "Public and prostitute",
        "cock": ("black", "white", "thick", "stranger", "hard"),
        "role": ("prostitute", "whore", "public", "gloryhole", "street", "rented"),
        "scene": ("public", "street", "park", "alley", "gloryhole", "corner", "restroom", "laundromat", "taxi"),
        "result": ("crowd", "watch", "film", "public", "pass", "street"),
        "passive": ("used", "passed", "fucked", "drilled", "pounded", "bred"),
        "active": ("suck", "gag", "swallow", "lick", "chok"),
        "toy": ("plug", "dildo", "vibrat"),
    },
    "toys": {
        "label": "Toys and stretching",
        "cock": ("black", "white", "thick", "massive", "monster"),
        "role": ("sissy", "trans", "plugged", "toy", "fuckpet", "cumslut"),
        "scene": ("motel", "bedroom", "bathroom", "shower"),
        "result": ("stretch", "plug", "gape", "leak", "toy"),
        "passive": ("stretched", "reamed", "pounded", "used", "fucked"),
        "active": ("ride", "suck", "lick", "stroke", "play"),
        "toy": ("plug", "dildo", "machine", "inflatable", "wand", "bead", "egg", "tentacle"),
    },
    "atm_cumdump": {
        "label": "Ass-to-mouth and cumdump",
        "cock": ("black", "white", "thick", "massive", "mixed"),
        "role": ("cumdump", "cumtoilet", "cumslave", "cumrag", "sponge", "ass-to-mouth"),
        "scene": ("party", "motel", "bathroom", "mattress", "alley"),
        "result": ("cum", "load", "face", "mouth", "bukkake", "creampie", "swallow"),
        "passive": ("bred", "creampied", "filled", "hosed", "used", "fucked"),
        "active": ("swallow", "lick", "suck", "gag", "chok"),
        "toy": ("plug", "dildo", "bowl"),
    },
}


FALLBACKS = {
    "roles": [
        "worthless sissy whore", "brainless bimbo cumslut", "desperate cumdump",
        "cheap street prostitute", "gaping anal slut", "humiliated public whore",
        "gagging deepthroat slut", "drooling anal addict", "eager cum sponge",
        "used-up sissy fuckpet", "cock-drunk street whore", "bukkake cumtoilet",
    ],
    "subjects": [
        "that massive big black cock", "that throbbing BBC", "a heavy black shaft",
        "that massive big white cock", "a fat veiny BWC", "that monster cock",
        "a pair of hard mixed cocks", "a line of strangers' cocks",
    ],
    "scenes": [
        "in a motel room", "at the public gloryhole", "in the alley",
        "at the truck-stop showers", "on a bare mattress", "in the bathroom stall",
    ],
    "toys": [
        "a massive knotted dildo", "an inflatable buttplug", "a thrusting dildo",
        "a thick double-ended dildo", "a weighted plug", "a vibrating wand",
    ],
    "results": [
        "until my eyes watered", "with spit running down my chin",
        "until my throat was raw", "with cum running down my thighs",
        "until my asshole gaped", "while strangers watched", "until my legs shook",
    ],
    "names": ["Ashley", "Trina", "Chloe", "Brittany", "Jessica", "Tiffany", "Amber", "Raven"],
    "active_verbs": ["sucked", "gagged on", "deepthroated", "swallowed", "licked", "choked on"],
    "passive_verbs": [
        "got face fucked by", "got my asshole stretched by", "got drilled by",
        "got passed around by", "got bred by", "got pounded by",
    ],
    "riding_verbs": ["rode", "bounced on", "squatted on", "backed my ass onto"],
    "contexts": [
        "until my jaw ached", "while spit ran down my chin", "until I was shaking",
        "with my makeup running", "while everyone watched", "until I begged for more",
    ],
    "extras": [
        "with my makeup running", "with my hands tied behind my back",
        "with spit hanging off my chin", "with a plug keeping my other hole open",
        "after being passed around", "with my collar pulled tight",
    ],
}

SIMPLE_TEMPLATES = (
    "I{name_tag} {active} {cock}{scene}, {result}.",
    "I{name_tag} {passive} {cock}{scene}, {result}.",
    "I{name_tag} {riding} {cock}{scene}, {result}.",
    "I{name_tag} {active} {cock} like {role}, {extra}.",
    "I{name_tag} got used like {role} and {active} {cock}, {result}.",
)

RICH_TEMPLATES = (
    "I{name_tag} {active} {cock}{scene}, then {passive} {cock2}, {result}.",
    "I{name_tag} {active} {cock} like {role}, then {riding} {cock2}, {extra}.",
    "I{name_tag} shoved {toy} up my ass before I {active} {cock}, {result}.",
    "I{name_tag} {passive} {cock}{scene}, my throat raw and my ass still aching, {result}.",
    "I{name_tag} took {cock} in my mouth, then {riding} {cock2} like {role}, {extra}.",
)

CORPUS_FILES = (
    "dirty_sentences.txt", "dirty_phrases.txt", "explicit_phrases01.txt",
    "explicit_phrases2.txt", "200_dirty_phrases.txt", "dirty_raw_sentences.txt",
)


def read_file(name: str) -> list[str]:
    """Read either plain lines or values from ``key | value`` data files."""
    output: list[str] = []
    for folder in DATA_DIRS:
        path = folder / name
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except (OSError, UnicodeError):
            continue
        for raw in lines:
            line = raw.strip()
            if not line or line.startswith("#") or line.startswith("["):
                continue
            if "|" in line:
                _key, value = line.split("|", 1)
                line = value.strip()
            if line:
                output.append(line)
    return unique(output)


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.casefold().strip()
        if key and key not in seen:
            seen.add(key)
            result.append(item.strip())
    return result


def pool(name: str) -> list[str]:
    return read_file(name) or FALLBACKS.get(name, [])


def choose(items: list[str], filters: tuple[str, ...] = (), fallback: str = "") -> str:
    narrowed = [item for item in items if any(term.casefold() in item.casefold() for term in filters)] if filters else []
    if narrowed:
        return random.choice(narrowed)
    if filters:
        return fallback or (random.choice(items) if items else "")
    return random.choice(items) if items else fallback


def choose_cock(category: str) -> str:
    spec = CATEGORIES[category]
    candidates = pool("subjects")
    matches = [item for item in candidates if any(term in item.casefold() for term in spec["cock"])]
    if category == "group":
        group_phrases = [item for item in candidates if any(term in item.casefold()
                         for term in ("pair", "two", "three", "line", "train", "mixed", "rotation"))]
        if group_phrases:
            matches = group_phrases
    if not matches:
        matches = [item for item in FALLBACKS["subjects"]
                   if any(term in item.casefold() for term in spec["cock"])]
    if not matches:
        matches = FALLBACKS["subjects"]
    return random.choice(matches)


def article(phrase: str) -> str:
    first = phrase.strip().split(maxsplit=1)[0] if phrase.strip() else "whore"
    return "an" if first[0].lower() in "aeiou" else "a"


def choose_role(category: str) -> str:
    spec = CATEGORIES[category]
    role = choose(pool("roles"), spec["role"], "desperate whore")
    return f"{article(role)} {role}"


def choose_scene(category: str) -> str:
    spec = CATEGORIES[category]
    scene = choose(pool("scenes"), spec["scene"], "in a motel room")
    if scene and scene[0].isalpha() and not scene.startswith(("in ", "at ", "on ", "behind ", "under ")):
        scene = "in " + scene
    return scene


def choose_result(category: str) -> str:
    spec = CATEGORIES[category]
    return choose(pool("contexts") + pool("ends") + FALLBACKS["results"], spec["result"], "until I was shaking")


def choose_active(category: str) -> str:
    terms = CATEGORIES[category]["active"]
    return choose(pool("active_verbs"), terms, "sucked")


def choose_passive(category: str) -> str:
    terms = CATEGORIES[category]["passive"]
    return choose(pool("passive_verbs"), terms, "got fucked by")


def choose_riding(category: str) -> str:
    return choose(pool("riding_verbs"), (), "rode")


def name_tag(names: list[str]) -> tuple[str, str]:
    """Return a first-person appositive occasionally, keeping every line in I POV."""
    name = random.choice(names) if names else random.choice(FALLBACKS["names"])
    return (f", {name},", name) if random.random() < 0.22 else ("", name)


def fill(template: str, values: dict[str, str]) -> str:
    text = template
    for _ in range(10):
        updated = TOKEN.sub(lambda match: values.get(match.group(1), ""), text)
        if updated == text:
            break
        text = updated
    text = re.sub(r"\s+([,.;])", r"\1", text)
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r"\s+", " ", text).strip(" ,")
    return text[0].upper() + text[1:] if text else text


def polish(sentence: str) -> str:
    sentence = re.sub(r"\s+([,.;!?])", r"\1", " ".join(sentence.split()))
    sentence = re.sub(r"([.!?])(?:[.!?])+", r"\1", sentence)
    if sentence and sentence[0].islower():
        sentence = sentence[0].upper() + sentence[1:]
    if sentence and not sentence.endswith((".", "!", "?")):
        sentence += "."
    return sentence


def corpus_sentence(category: str) -> str | None:
    """Occasionally reuse a finished first-person sentence from the data lists."""
    if random.random() >= 0.16:
        return None
    spec = CATEGORIES[category]
    corpus: list[str] = []
    for filename in CORPUS_FILES:
        corpus.extend(read_file(filename))
    corpus = [line for line in unique(corpus)
              if re.match(r"^(I\b|I'm\b|I've\b|My\b)", line, flags=re.IGNORECASE)]
    if not corpus:
        return None
    terms = spec["cock"] + spec["role"] + spec["result"] + spec["scene"]
    matches = [line for line in corpus if any(term in line.casefold() for term in terms)]
    return polish(random.choice(matches)) if matches else None


def build_sentence(category: str, intensity: int = 2) -> str:
    spec = CATEGORIES[category]
    raw_sentence = corpus_sentence(category)
    if raw_sentence:
        return raw_sentence

    scene = choose_scene(category)
    if scene:
        scene = " " + scene
    tag, _name = name_tag(pool("names"))
    cock = choose_cock(category)
    values = {
        "name_tag": tag,
        "active": choose_active(category),
        "passive": choose_passive(category),
        "riding": choose_riding(category),
        "cock": cock,
        "cock2": choose_cock(category),
        "scene": scene,
        "role": choose_role(category),
        "result": choose_result(category).rstrip(".!?"),
        "extra": choose(pool("contexts") + FALLBACKS["extras"], spec["result"], "with spit running down my chin").rstrip(".!?"),
        "toy": choose(pool("toys"), spec["toy"], "a thick dildo"),
    }

    rich_chance = {1: 0.12, 2: 0.30, 3: 0.48}[intensity]
    template = random.choice(RICH_TEMPLATES if random.random() < rich_chance else SIMPLE_TEMPLATES)
    sentence = polish(fill(template, values))

    # Keep intensity 1 concise; at higher levels add an occasional short second
    # sentence, while the main sentence stays grammatically self-contained.
    if intensity >= 2 and random.random() < (0.08 if intensity == 2 else 0.20):
        followup = choose(pool("ends") + FALLBACKS["results"], spec["result"], "I asked for more")
        followup = polish(followup)
        sentence = sentence.rstrip(".") + ". " + followup
    return sentence


def generate(count: int = 50, category: str = "all", intensity: int = 2) -> list[str]:
    if count < 0:
        raise ValueError("count must be 0 or greater")
    if category not in CATEGORIES and category != "all":
        raise ValueError(f"Unknown category: {category}")
    output: list[str] = []
    seen: set[str] = set()
    attempts = 0
    limit = max(500, count * 80)
    names = list(CATEGORIES) if category == "all" else [category]
    while len(output) < count and attempts < limit:
        attempts += 1
        selected = random.choice(names)
        sentence = build_sentence(selected, intensity)
        key = sentence.casefold()
        if key not in seen:
            seen.add(key)
            output.append(sentence)
    return output


def render(sentences: list[str], output_format: str) -> str:
    if output_format == "json":
        return json.dumps({"generator": f"Dirty Generator {VERSION}", "count": len(sentences),
                           "sentences": sentences}, indent=2, ensure_ascii=False)
    if output_format == "md":
        return f"# Dirty Generator {VERSION}\n\n" + "\n".join(
            f"{index}. {sentence}" for index, sentence in enumerate(sentences, 1)) + "\n"
    if output_format == "html":
        items = "\n".join(f"<li>{html.escape(sentence)}</li>" for sentence in sentences)
        return ("<!doctype html><html lang=\"en\"><meta charset=\"utf-8\"><title>Dirty Generator "
                f"{VERSION}</title><body><h1>Dirty Generator {VERSION}</h1><ol>{items}</ol></body></html>\n")
    return "\n".join(f"{index}. {sentence}" for index, sentence in enumerate(sentences, 1)) + "\n"


def list_categories() -> None:
    for key, spec in CATEGORIES.items():
        print(f"{key:<16} {spec['label']}")
    print(f"{'all':<16} Randomly select one category per sentence")


def menu() -> int:
    while True:
        print(f"\nDIRTY GENERATOR {VERSION}\n1. Generate 50 sentences across categories\n2. List categories\n0. Exit")
        choice = input("> ").strip()
        if choice == "0":
            return 0
        if choice == "1":
            print(render(generate(50, "all", 2), "txt"))
        elif choice == "2":
            list_categories()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate focused first-person Dirty Generator sentences.")
    parser.add_argument("-n", "--count", type=int, default=50, help="number of unique sentences (default: 50)")
    parser.add_argument("-c", "--category", default="all", choices=(*CATEGORIES, "all"))
    parser.add_argument("-x", "--intensity", type=int, default=2, choices=(1, 2, 3))
    parser.add_argument("-f", "--format", default="txt", choices=("txt", "md", "html", "json"))
    parser.add_argument("-o", "--out", help="save output to a file")
    parser.add_argument("--seed", type=int, help="repeatable random seed")
    parser.add_argument("--list-categories", action="store_true")
    args = parser.parse_args(argv)
    if args.list_categories:
        list_categories()
        return 0
    if args.seed is not None:
        random.seed(args.seed)
    content = render(generate(args.count, args.category, args.intensity), args.format)
    if args.out:
        destination = Path(args.out).expanduser()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        print(f"Saved {args.count} requested sentences to {destination}")
    else:
        print(content.rstrip())
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        raise SystemExit(menu())
    raise SystemExit(main())

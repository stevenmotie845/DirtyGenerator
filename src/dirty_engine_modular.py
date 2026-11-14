#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data-driven sentence and story generator for DirtyGenerator.

Data is read from ``src/data`` when present, with ``data`` at the repository
root as a fallback. Vocabulary files may be plain one-item-per-line lists or
pipe-delimited pools. ``templates.txt`` uses INI-style section headers.
"""
from __future__ import annotations

import argparse
import html
import json
import random
import re
import sys
from pathlib import Path
from typing import Iterable


VERSION = "10.1"
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
DATA_DIR = SCRIPT_DIR / "data"
if not (DATA_DIR / "templates.txt").is_file():
    DATA_DIR = ROOT_DIR / "data"

TOKEN = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")

CATEGORIES = ("bbc", "bwc", "any", "group", "oral", "atm", "public", "prostitution", "toys")
CATEGORY_TAGS = {"bbc": "bbc", "bwc": "bwc", "any": "any"}
VERB_FILTERS = {
    "group": ("gang", "dp'd", "tp'd", "spit roasted", "passed", "drilled", "airtight"),
    "oral": ("throat", "mouth", "face", "gag"),
    "atm": ("creampied", "bred", "pumped full", "hosed", "ass"),
}
THEMES = {
    "gloryhole": ("gloryhole", "bathroom", "rest-stop"),
    "party": ("party", "balcony", "mattress"),
    "reststop": ("rest-stop", "truck", "shower"),
    "upside": ("upside",),
    "sissy": ("collar", "socks", "lace"),
    "street": ("alley", "doorway", "counter", "corner"),
    "motel": ("motel", "mattress"),
    "sauna": ("sauna", "shower"),
    "salon": ("salon",),
    "gangbang": ("eight", "ten", "dozen", "fifteen"),
    "cumswap": ("swapped", "licked", "slurped"),
    "laundromat": ("laundromat", "stairwell", "taxi"),
}

# Pool files contain the original, detailed lists. pools.txt remains supported
# as an override/addition for users who prefer a single categorized vocabulary.
POOL_FILES = {
    "actions": "actions.txt",
    "balls": "balls.txt",
    "clothing": "clothing.txt",
    "cum": "cum.txt",
    "dirty_ass": "dirty_ass.txt",
    "eat_cum": "eat_cum.txt",
    "ends": "ends.txt",
    "fluids": "fluids.txt",
    "gag_verbs": "gag_verbs.txt",
    "gangbang_terms": "gangbang_terms.txt",
    "holes": "holes.txt",
    "names": "names.txt",
    "numbers": "numbers.txt",
    "oral_tails": "oral_tails.txt",
    "participles": "participles.txt",
    "passive_verbs": "passive_verbs.txt",
    "pets": "pets.txt",
    "places": "places.txt",
    "positions": "positions.txt",
    "reactions": "reactions.txt",
    "reasons": "reasons.txt",
    "riding_verbs": "riding_verbs.txt",
    "rim": "rim.txt",
    "roles": "roles.txt",
    "scenes": "scenes.txt",
    "seconds": "seconds.txt",
    "smells": "smells.txt",
    "sounds": "sounds.txt",
    "subjects": "subjects.txt",
    "throat_verbs": "throat_verbs.txt",
    "titles": "titles.txt",
    "toys": "toys.txt",
}

POOL_ALIASES = {
    "fluids": ("fluids", "fluid"),
    "numbers": ("numbers", "number"),
    "reactions": ("reactions", "reaction"),
    "reasons": ("reasons", "reason"),
    "gangbang_terms": ("gangbang_terms", "terms", "term"),
    "oral_tails": ("oral_tails", "tails", "tail"),
    "places": ("places", "place"),
    "positions": ("positions", "position"),
    "roles": ("roles", "role"),
    "smells": ("smells", "smell"),
}


def read_lines(filename: str) -> list[str]:
    """Read non-empty UTF-8 lines, ignoring comments and Mac metadata files."""
    path = DATA_DIR / filename
    if not path.is_file():
        return []
    try:
        content = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise RuntimeError(f"Could not read data file {path}: {exc}") from exc
    return [line.strip() for line in content.splitlines()
            if line.strip() and not line.lstrip().startswith("#")]


def read_index(filename: str) -> dict[str, list[str]]:
    """Read either ``key | value`` rows or sectioned template files."""
    groups: dict[str, list[str]] = {}
    section: str | None = None
    for line in read_lines(filename):
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip().lower()
        elif "|" in line:
            key, value = line.split("|", 1)
            key, value = key.strip().lower(), value.strip()
            if key and value:
                groups.setdefault(key, []).append(value)
        elif section:
            groups.setdefault(section, []).append(line)
    return groups


POOLS = read_index("pools.txt")
VERBS = read_index("verbs.txt")
TEMPLATES = read_index("templates.txt")

DEFAULT_VERBS = {
    "active": ["sucked", "deepthroated", "gagged on", "swallowed", "licked"],
    "passive": ["got fucked by", "was drilled by", "got face fucked by"],
    "riding": ["rode", "bounced on", "grinded on"],
}
for _kind, _defaults in DEFAULT_VERBS.items():
    if not VERBS.get(_kind):
        source_file = {"active": "active_verbs.txt", "passive": "passive_verbs.txt",
                       "riding": "riding_verbs.txt"}[_kind]
        VERBS[_kind] = read_lines(source_file) or _defaults

DEFAULT_TEMPLATES = {
    "short": ["I {av} {cock1}.", "I {av} {every}.", "I {av} {cocks}."],
    "story_open": ["{Subj} arrived at {place} for {reason}."] ,
    "story_beat": ["{Subj} {action} {subject} at {place}, then asked for more."],
    "story_name": ["{Name} {action} {subject} and kept going."],
    "story_close": ["{Subj} left {place}, exhausted but satisfied."],
}
for _family, _templates in DEFAULT_TEMPLATES.items():
    if not TEMPLATES.get(_family):
        TEMPLATES[_family] = _templates


def _unique(items: Iterable[str]) -> list[str]:
    found: set[str] = set()
    result: list[str] = []
    for item in items:
        cleaned = item.strip()
        key = cleaned.casefold()
        if cleaned and key not in found:
            found.add(key)
            result.append(cleaned)
    return result


def pool(name: str) -> list[str]:
    """Combine the matching categorized pool and its dedicated text file."""
    aliases = POOL_ALIASES.get(name, (name,))
    items: list[str] = []
    for alias in aliases:
        items.extend(POOLS.get(alias, []))
    filename = POOL_FILES.get(name)
    if filename:
        items.extend(read_lines(filename))
    return _unique(items)


def indexed_lines(filename: str, key: str) -> list[str]:
    """Use categorized entries when present; otherwise read a plain list."""
    parsed = read_index(filename)
    if parsed.get(key):
        return parsed[key]
    return read_lines(filename)


COCK_ROWS: list[tuple[str, set[str]]] = []
for _line in read_lines("cocks.txt"):
    if "|" in _line:
        _adjective, _tags = _line.split("|", 1)
        _adjective = _adjective.strip()
        _tag_set = {tag.strip().lower() for tag in _tags.split(",") if tag.strip()}
        if _adjective:
            COCK_ROWS.append((_adjective, _tag_set))
if not COCK_ROWS:
    COCK_ROWS = [("thick veiny", {"any"}), ("massive black", {"bbc", "any"}),
                 ("massive white", {"bwc", "any"}), ("throbbing", {"any"})]


def article(phrase: str) -> str:
    first_word = phrase.strip().split(maxsplit=1)[0] if phrase.strip() else "thing"
    return "an" if first_word[0].lower() in "aeiou" else "a"


def choose(items: list[str], default: str, filters: tuple[str, ...] | None = None) -> str:
    if filters:
        filtered = [item for item in items if any(term in item.casefold() for term in filters)]
        if filtered:
            items = filtered
    return random.choice(items) if items else default


def cock_phrase(tag: str | None = None, style: str | None = None,
                noun: str | None = None) -> str:
    noun = noun or random.choice(("cock", "dick"))
    rows = COCK_ROWS
    if tag and tag != "any":
        tagged = [(adj, tags) for adj, tags in rows if tag in tags or "any" in tags]
        if tagged:
            rows = tagged
    adjective, _tags = random.choice(rows)
    if style is None:
        roll = random.random()
        style = "single" if roll < .24 else "digit" if roll < .36 else \
                "word" if roll < .50 else "everyone" if roll < .72 else "bare"
    if style == "single":
        return f"{article(adjective)} {adjective} {noun}"
    if style == "digit":
        return f"{random.randint(2, 9)} {adjective} {noun}s"
    if style == "word":
        return f"{random.choice(('two', 'three', 'four', 'five', 'six', 'eight', 'ten'))} {adjective} {noun}s"
    if style == "everyone":
        return f"everyone's {adjective} {noun}"
    return f"{adjective} {noun}s"


def fill(template: str, values: dict[str, str]) -> str:
    """Resolve nested tokens such as ``{poss}`` inside vocabulary entries."""
    text = template
    for _ in range(20):
        updated = TOKEN.sub(lambda match: values.get(match.group(1), match.group(0)), text)
        if updated == text:
            break
        text = updated
    return text


def capitalize(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def polish(text: str) -> str:
    text = " ".join(text.split())
    text = re.sub(r"\s+([,.;!?])", r"\1", text)
    text = re.sub(r"([.!?])(?:[.!?])+", r"\1", text)
    return capitalize(text) + ("" if text.endswith((".", "!", "?")) else ".")


def make_slots(tag: str | None = None, first_person: bool = True,
               name: str = "") -> dict[str, str]:
    noun = random.choice(("cock", "dick"))
    subject = "I" if first_person else (name or "she")
    pronoun = "my" if first_person else "her"
    object_pronoun = "me" if first_person else "her"

    values: dict[str, str] = {
        "poss": pronoun, "obj": object_pronoun, "subj": subject,
        "Subj": capitalize(subject), "Name": name or "Ashley", "name": name or "Ashley",
        "be": "am" if first_person else "is", "word": noun,
        "cock1": cock_phrase(tag, "single", noun),
        "cock2": cock_phrase(tag, "single", noun),
        "cock3": cock_phrase(tag, "single", noun),
        "every": cock_phrase(tag, "everyone", noun),
        "cocks": cock_phrase(tag, None, noun),
    }

    defaults = {
        "actions": "used", "balls": "his balls", "clothing": "nothing but a collar",
        "cum": "a warm load", "dirty_ass": f"{pronoun} dirty asshole",
        "eat_cum": "I swallowed every drop", "ends": "until my eyes watered",
        "fluids": "thick ropes of cum", "gag_verbs": "gagged",
        "gangbang_terms": "gangbang", "holes": f"{pronoun} asshole",
        "names": "Ashley", "numbers": "several", "oral_tails": "",
        "participles": "spit running down my chin", "passive_verbs": "got fucked by",
        "pets": "his toy", "places": "the motel", "positions": "on my knees",
        "reactions": "shook", "reasons": "the money", "riding_verbs": "rode",
        "rim": "I rimmed him", "roles": "whore", "scenes": "",
        "seconds": "", "smells": "funky", "sounds": "wet slaps",
        "subjects": f"that massive {noun}", "throat_verbs": "slammed down my throat",
        "titles": "", "toys": "a thick dildo",
    }
    for key, fallback in defaults.items():
        values[key] = choose(pool(key), fallback)

    # Short aliases match the names used in templates.txt.
    aliases = {
        "action": "actions", "actor": "roles", "ass": "dirty_ass", "end": "ends",
        "fluid": "fluids", "gv": "gag_verbs", "n2": "numbers", "number": "numbers",
        "part": "participles", "pet": "pets", "place": "places", "position": "positions",
        "reaction": "reactions", "reason": "reasons", "subject": "subjects",
        "term": "gangbang_terms", "toy": "toys", "tv": "throat_verbs",
        "tail": "oral_tails", "smell": "smells",
    }
    for alias, source in aliases.items():
        values[alias] = values[source]

    # Article-prefixed role is useful in templates such as "like {role}".
    role_text = values["roles"]
    values["role"] = f"{article(role_text)} {role_text}"
    values["ass"] = fill(values["ass"], values)
    values["Ass_cap"] = capitalize(values["ass"])
    values["Poss_ass"] = capitalize(values["ass"])
    values["scene"] = f" {values['scenes']}" if values["scenes"] else ""
    values["tail"] = f" {values['oral_tails']}" if values["oral_tails"] else ""

    # Ensure template values which themselves contain tokens are resolved.
    for key, value in tuple(values.items()):
        if TOKEN.search(value):
            values[key] = fill(value, values)
    return values


def get_template(family: str, fallback: str = "short") -> str:
    family = family.lower()
    candidates = TEMPLATES.get(family) or TEMPLATES.get(fallback) or DEFAULT_TEMPLATES["short"]
    return random.choice(candidates)


def choose_family(intensity: int) -> str:
    # The richer families become more common as intensity increases.
    weights = {
        1: (("short", 55), ("riding", 20), ("special", 15), ("rich", 10)),
        2: (("short", 30), ("riding", 15), ("special", 20), ("rich", 35)),
        3: (("short", 15), ("riding", 10), ("special", 25), ("rich", 50)),
    }[intensity]
    available = [(family, weight) for family, weight in weights
                 if TEMPLATES.get(family)]
    return random.choices([item[0] for item in available],
                          weights=[item[1] for item in available], k=1)[0]


def make_sentence(category: str = "any", intensity: int = 2) -> str:
    tag = CATEGORY_TAGS.get(category)
    values = make_slots(tag)
    family = choose_family(intensity)
    values["av"] = choose(VERBS.get("active", []), "sucked")
    values["pv"] = choose(VERBS.get("passive", []), "got fucked by",
                          VERB_FILTERS.get(category))
    values["rv"] = choose(VERBS.get("riding", []), "rode")
    template = get_template(family)
    return polish(fill(template, values))


def generate(count: int = 50, category: str = "any", intensity: int = 2) -> list[str]:
    if count < 0:
        raise ValueError("count must be zero or greater")
    if category not in CATEGORIES and category != "all":
        raise ValueError(f"unknown category: {category}")
    generated: list[str] = []
    seen: set[str] = set()
    attempts = 0
    max_attempts = max(count * 100, 1000)
    while len(generated) < count and attempts < max_attempts:
        attempts += 1
        chosen_category = random.choice(CATEGORIES) if category == "all" else category
        sentence = make_sentence(chosen_category, intensity)
        if sentence.casefold() not in seen:
            seen.add(sentence.casefold())
            generated.append(sentence)
    return generated


def story(beats: int = 8, theme: str = "random", pov: str = "third",
          intensity: int = 2) -> str:
    first_person = pov == "first"
    names = pool("names")
    titles = pool("titles")
    name = random.choice(names) if names else "Ashley"
    title = random.choice(titles) if titles and random.random() < .5 else ""
    theme_keys = THEMES.get(theme)

    def story_slots() -> dict[str, str]:
        values = make_slots(first_person=first_person, name=name)
        if theme_keys:
            for key in ("places", "clothing", "numbers", "positions", "toys"):
                options = pool(key)
                matching = [item for item in options
                            if any(term in item.casefold() for term in theme_keys)]
                if matching:
                    values[key] = random.choice(matching)
                    alias = {"places": "place", "positions": "position",
                             "numbers": "number", "toys": "toy"}.get(key, key)
                    values[alias] = values[key]
        return values

    parts = [fill(get_template("story_open", "short"), story_slots())]
    for index in range(max(1, beats)):
        family = "story_name" if index in (2, 6) and not first_person and random.random() < .25 else "story_beat"
        parts.append(fill(get_template(family, "short"), story_slots()))
        if intensity >= 3 and random.random() < .25:
            reaction = choose(pool("reactions"), "shook")
            parts.append(fill(reaction, story_slots()))
    parts.append(fill(get_template("story_close", "short"), story_slots()))
    heading = capitalize(theme if theme != "random" else "dirty story")
    who = f"{title} {name}".strip() if title else name
    body = "\n\n".join(polish(part) for part in parts if part.strip())
    return f"=== {heading}: {who} ===\n\n{body}\n"


HTML_TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dirty Engine __VERSION__</title><style>
body{background:#111;color:#eee;font:17px/1.7 Georgia,serif;margin:0;padding:2rem}
h1{font-size:1.1rem;letter-spacing:.14em;text-transform:uppercase;color:#e8557f}
ol,p{max-width:58rem}li{margin-bottom:.8rem;padding-bottom:.8rem;border-bottom:1px solid #262626}
p{text-indent:1.4em}</style></head><body><h1>Dirty Engine __VERSION__</h1>__BODY__</body></html>"""


def render(items: list[str] | str, output_format: str, story_mode: bool = False) -> str:
    if story_mode:
        story_text = str(items)
        if output_format == "json":
            return json.dumps({"story": story_text}, indent=2, ensure_ascii=False)
        if output_format == "html":
            body = "".join(f"<p>{html.escape(part)}</p>" for part in story_text.split("\n\n"))
            return HTML_TEMPLATE.replace("__VERSION__", VERSION).replace("__BODY__", body)
        return story_text

    sentences = list(items)  # type: ignore[arg-type]
    if output_format == "json":
        return json.dumps({"count": len(sentences), "sentences": sentences},
                          indent=2, ensure_ascii=False)
    if output_format == "md":
        return f"# Dirty Engine {VERSION}\n\n" + "\n".join(
            f"{index}. {sentence}" for index, sentence in enumerate(sentences, 1)) + "\n"
    if output_format == "html":
        body = "<ol>" + "".join(f"<li>{html.escape(sentence)}</li>" for sentence in sentences) + "</ol>"
        return HTML_TEMPLATE.replace("__VERSION__", VERSION).replace("__BODY__", body)
    return "\n".join(f"{index}. {sentence}" for index, sentence in enumerate(sentences, 1)) + "\n"


def status() -> str:
    lines = [f"Data folder: {DATA_DIR}", "Loaded files:"]
    for filename in ("templates.txt", "pools.txt", "verbs.txt", "cocks.txt"):
        lines.append(f"  {filename:<18} {len(read_lines(filename)):>4} lines")
    lines.append("Template sections: " + ", ".join(sorted(TEMPLATES)))
    lines.append("Vocabulary pools: " + ", ".join(
        f"{name}={len(pool(name))}" for name in sorted(POOL_FILES)))
    return "\n".join(lines)


def check_data() -> list[str]:
    errors: list[str] = []
    if not read_lines("templates.txt"):
        errors.append("templates.txt is missing or empty")
    if not read_lines("cocks.txt"):
        errors.append("cocks.txt is missing or empty; built-in fallback will be used")
    required_sections = ("short", "rich", "special", "riding")
    for section in required_sections:
        if not TEMPLATES.get(section):
            errors.append(f"templates.txt has no [{section}] section; fallback templates will be used")
    known = set(make_slots().keys()) | {"av", "pv", "rv"}
    for section, templates in TEMPLATES.items():
        for line_number, template in enumerate(templates, 1):
            unknown = sorted(set(TOKEN.findall(template)) - known)
            if unknown:
                errors.append(f"[{section}] template {line_number} uses unknown token(s): {', '.join(unknown)}")
    return errors


def menu() -> int:
    while True:
        print(f"\nDIRTY ENGINE v{VERSION}\n1. Generate sentences\n2. Generate a story\n3. Show data status\n0. Exit")
        choice = input("> ").strip()
        if choice == "0":
            return 0
        if choice == "1":
            print(render(generate(50), "txt"))
        elif choice == "2":
            theme = input("Theme (blank for random): ").strip() or "random"
            print(story(theme=theme if theme in THEMES else "random"))
        elif choice == "3":
            print(status())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate sentences or short stories from the data folder.")
    parser.add_argument("-n", "--count", type=int, default=None, help="number of unique sentences")
    parser.add_argument("-c", "--category", default="any", choices=(*CATEGORIES, "all"))
    parser.add_argument("-s", "--story", action="store_true", help="generate a short story")
    parser.add_argument("-t", "--theme", default="random", choices=(*THEMES, "random"))
    parser.add_argument("-b", "--beats", type=int, default=8)
    parser.add_argument("--pov", default="third", choices=("first", "third"))
    parser.add_argument("-x", "--intensity", type=int, default=2, choices=(1, 2, 3))
    parser.add_argument("-o", "--out", help="write output to a file")
    parser.add_argument("-f", "--format", default="txt", choices=("txt", "md", "html", "json"))
    parser.add_argument("--seed", type=int, help="set a repeatable random seed")
    parser.add_argument("--status", action="store_true", help="show loaded data files and pools")
    parser.add_argument("--check", action="store_true", help="check data files and template tokens")
    args = parser.parse_args(argv)

    if args.status:
        print(status())
        return 0
    if args.check:
        errors = check_data()
        if errors:
            print("Data check found issues:")
            for error in errors:
                print(f"- {error}")
            return 1
        print("Data files and template tokens look good.")
        return 0
    if args.seed is not None:
        random.seed(args.seed)

    if args.story:
        output = render(story(args.beats, args.theme, args.pov, args.intensity), args.format, True)
    else:
        count = args.count if args.count is not None else 50
        output = render(generate(count, args.category, args.intensity), args.format)

    if args.out:
        destination = Path(args.out).expanduser()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output, encoding="utf-8")
        print(f"Saved output to {destination}")
    else:
        print(output.rstrip())
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        raise SystemExit(menu())
    raise SystemExit(main())

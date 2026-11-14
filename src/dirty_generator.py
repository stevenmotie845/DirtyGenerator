#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dirty Generator 2.0
===================

Uncensored first-person 10/10-graphic phrase combinator.

Fragment pools (BBC, BWC, sissy, bimbo, anal stretching, cum dripping,
bukkake, DP/TP, ATM, toys, public gloryhole, prostitute, trans, gagging,
creampie) are woven through grammatical templates so every output is a real
sentence instead of comma-spliced word salad.

Fixed vs 1.0:
  * every filter falls back safely -- no IndexError on an empty pool
  * templates rewritten so each slot has a strict grammatical contract
  * swallowed `phrase.replace(...)` line restored, whitespace normalised
  * duplicate suppression, seeding, CLI flags, txt/md/html/json export
  * menu is optional; the script also runs fully non-interactive

Usage:
    python dirty_generator.py                        # interactive menu
    python dirty_generator.py -n 400 -o out.txt      # batch + save
    python dirty_generator.py -c bbc_anal -n 20
    python dirty_generator.py -f html -o gallery.html -c all
    python dirty_generator.py --list-categories
"""

from __future__ import annotations

import argparse
import html
import json
import random
import re
import sys
from pathlib import Path

VERSION = "2.0"
DEFAULT_FILE = "dirty_phrases.txt"

# --------------------------------------------------------------------------
# Fragment pools. Contract per slot:
#   role   -> bare noun phrase (article added at pick time)
#   cock   -> noun phrase, article baked in
#   oral   -> past-tense verb phrase, first person
#   fuck   -> past-tense verb phrase, first person
#   scene  -> prepositional phrase
#   toy    -> noun phrase, article baked in
#   result -> clause used after a comma, lowercase participle
#   extra  -> modifier phrase used after a comma
# --------------------------------------------------------------------------

ROLES = [
    "worthless sissy whore",
    "brainless bimbo cumslut",
    "pathetic transgender cumslave",
    "cheap street prostitute",
    "gaping anal slut",
    "desperate gloryhole cumdump",
    "humiliated public whore",
    "stretched asshole slave",
    "gagging deepthroat slut",
    "bukkake-covered cumtoilet",
    "leaking creampie dump",
    "clitty-caged sissy pet",
    "fake-tit bimbo fucktoy",
    "ass-to-mouth filth whore",
    "triple-penetration cumrag",
    "drooling anal addict",
    "brain-dead cock sleeve",
    "rented gloryhole hole",
    "truck-stop cumdump",
    "bimbo breeding whore",
    "sissy anal cockslut",
    "public-use cumdump",
    "ATM-obsessed filth slut",
    "double-stuffed ass whore",
    "wrecked little sissy fuckpet",
    "cum-swapping cumslut",
    "plugged bimbo hole",
    "trans gloryhole regular",
    "cock-drunk street whore",
    "slobbering throat slave",
    "loose-holed anal whore",
    "eager little cum sponge",
    "braindead bukkake toy",
    "used-up sissy cuntboy",
    "milking-machine cumslut",
    "back-alley anal whore",
    "gagging bimbo cumdump",
    "swollen-holed fuckpet",
]

COCKS = [
    "that massive big black cock",
    "a throbbing huge white cock",
    "two mixed big black and big white cocks",
    "an enormous BBC stretching everything",
    "a fat veiny BWC",
    "anonymous gloryhole cocks, black and white both",
    "a monster black dick and a thick white one at once",
    "the biggest BBC I could gag on",
    "a train of strangers' mixed cocks",
    "a heavy-hanging black cock",
    "a pale, thick, uncut white cock",
    "a pair of hard mixed cocks",
    "a slick ebony cock",
    "a long pink white-boy cock",
    "a black cock thicker than my wrist",
    "a white cock so hard it slapped my cheek",
    "three strangers' cocks in rotation",
    "a big black cock and a fat white one together",
    "a line of cocks waiting behind me",
    "a sweaty stranger's cock",
    "a soft-then-iron-hard white cock",
    "a black cock with a vein running down it",
    "a fat-headed BWC",
    "two black cocks and one white",
    "a thick cock that split me open",
    "a hard young white cock",
]

ORAL = [
    "gagged violently until spit and puke ran down my chin while deepthroating",
    "sucked like a starving whore and took it straight ass-to-mouth",
    "deepthroated until my throat bulged and I choked on it",
    "gagged on it at the gloryhole with drool pouring off my chin",
    "swallowed it to the balls then licked it clean after it had been in my ass",
    "slobbered all over it and buried my nose in his balls",
    "choked on it until my eyes watered and my mascara ran",
    "took it down my throat in one push and held it there",
    "sucked two of them at once with a hand on each",
    "licked the shaft and sloppy-slurped the head until he groaned",
    "gagged myself on it over and over until I saw stars",
    "stuffed my throat full and hummed around it",
    "sucked it clean while a second one pushed at my lips",
    "drove it into my throat until I had to pull off for air",
    "made a wet mess of it, drooling and gulping",
    "took it all the way down and swallowed around the head",
    "let him face-fuck my throat like a toy",
    "sucked the cum out of it and held it in my cheeks",
    "lapped at the head and licked up the leaking precum",
    "gagged so hard my whole body jerked",
    "worked it in and out of my throat with my tongue flat",
    "swallowed around it while he held my head still",
    "slopped it against my cheek and slapped it with my tongue",
    "took it past my gag reflex and kept it there",
    "licked it from the balls up and moaned on the way",
    "sucked until my jaw ached and my chin was soaked",
]

FUCK = [
    "rode like a desperate bouncing slut until it wrecked me",
    "got my asshole stretched wide and pounded without mercy",
    "took it in double penetration, wrecking both holes at once",
    "was triple penetrated with two cocks and a huge dildo filling every inch",
    "backed my ass onto it in public while people watched",
    "bent over and took it balls-deep in one shove",
    "got pounded so hard my tits swung",
    "took it doggy-style with my face pushed into the dirt",
    "had my ass spread and drilled until I gaped",
    "got fucked on my back with my legs over his shoulders",
    "was used like a fleshlight and just held on",
    "took it slow and deep until I felt every inch",
    "bounced on it reverse cowgirl with my ass jiggling",
    "got railed standing up against the wall",
    "took a long, slow anal reaming",
    "spread my own cheeks and pushed back onto it",
    "got my hole stretched around the widest part and held there",
    "was passed between two of them and never got a break",
    "took it in the ass while a second one waited",
    "got my asshole reamed out until it gaped and winked",
    "was folded in half and fucked stupid",
    "rode it with my hands braced on his chest",
    "took it hard and fast until the sound was filthy",
    "got drilled from behind with a fist in my hair",
    "was bent over a knee and opened up slowly",
    "took it in every hole they wanted, in whatever order",
    "got my ass pounded while my plug popped out",
    "was held down and reamed until I was babbling",
]

SCENES = [
    "at the filthy public gloryhole",
    "in the alley while cars and people passed",
    "on the street corner working as a prostitute",
    "in the park bent over a bench for anyone to use",
    "in a motel room with toys already stretching me",
    "behind the dumpster like a cheap whore",
    "in the club bathroom stall with the door open",
    "in a dark cruise-bar back room",
    "on the hood of a stranger's car",
    "in the stairwell of the parking garage",
    "against a chain-link fence",
    "in the truck-stop showers",
    "on a picnic table in broad daylight",
    "in the back seat of a taxi",
    "at a highway rest stop",
    "under a bridge where the homeless sleep",
    "in the bushes at the edge of the park",
    "on the balcony with the city watching",
    "in the gym sauna",
    "on a bare mattress in a group house",
    "in the laundromat with the machines still running",
    "at a house party with everyone in the next room",
    "over a barstool with my skirt around my waist",
    "in a changing room with the curtain half open",
    "on the floor of a public restroom",
    "in the doorway of a shop after closing",
]

TOYS = [
    "a massive knotted dildo",
    "an inflatable buttplug pumped to the max",
    "a ribbed horse-cock dildo",
    "a thrusting fuck-machine dildo",
    "a stack of glass and silicone dildos",
    "a fist-sized plug and then the real thing",
    "a vibrating wand taped to a plug",
    "a tapered anal-trainer set, all at once",
    "a huge suction-cup dildo stuck to the tile",
    "a beaded steel plug pulled out one ball at a time",
    "a thick double-ended dildo",
    "a hollow plug that leaks lube",
    "a weighted egg plug",
    "a spinning, rotating anal toy",
    "a soft-then-hard inflatable plug",
    "a heavy steel plug with a jewel base",
    "a knotted tentacle dildo",
    "a fuck-machine with a suction mount",
    "a glass plug warmed under the tap",
    "a fat silicone dildo with a knot at the base",
]

RESULTS = [
    "until thick ropes of cum poured out of my gaping asshole",
    "leaving me a leaking mess of mixed loads running down my thighs",
    "as I became their total cumslave, face and tits glazed in bukkake",
    "with my locked clitty leaking pathetically the whole time",
    "with my holes ruined and gaping open for hours after",
    "turning me into a used toilet they all dumped in and on",
    "until I was cross-eyed and babbling like a brainless fucktoy",
    "with cum swapping from my ass straight into my mouth",
    "until my legs shook and gave out completely",
    "leaving a puddle of lube, spit and cum on the floor",
    "as everyone watched my holes get wrecked open",
    "until my voice was gone from gagging",
    "with creampie dripping down the inside of both thighs",
    "so everyone saw exactly what a cheap cumdump I am",
    "until my asshole was puffy and winking",
    "leaving my makeup smeared and my throat raw",
    "with cum still running out of me in the taxi home",
    "until I couldn't remember my own name",
    "with my tits and face painted in other men's cum",
    "until the only word left in my head was more",
    "leaving my plug back in just to keep the load inside",
    "with my ass red and my hole still twitching",
    "as they all lined up to finish on my face",
    "until I was a shivering, drooling wreck",
    "with the taste of ass still in my mouth",
    "leaving me sprawled out and used on the ground",
    "so my hole stayed wet and open long after they left",
    "until I thanked every one of them with a mouthful",
]

EXTRAS = [
    "in full sissy lingerie with my makeup running",
    "with a buttplug keeping my other hole stretched open",
    "after wrecking myself stupid with toys first",
    "with my fake bimbo tits bouncing and slick with spit",
    "as a transgender slut taking it in every hole I have",
    "publicly, so anyone passing could watch the humiliation",
    "with my caged clitty leaking down my thigh",
    "in heels and a short skirt hiked up over my ass",
    "with my makeup ruined and my hair a mess",
    "with spit ropes hanging off my chin",
    "still wearing my plug and dripping lube",
    "with a crowd of strangers watching and filming",
    "barely able to keep my eyes open",
    "with my ass already red from spanking",
    "after being passed around for an hour",
    "with my throat already raw from gagging",
    "with my bra pulled down under my tits",
    "in nothing but knee-high socks and a collar",
    "with a leash clipped to my collar",
    "with my tights torn open at the crotch",
    "smelling of lube, cum and cheap perfume",
    "with my hands tied behind my back",
    "in ruined drag makeup",
    "with a plug still humming on low inside me",
]

TEMPLATES = [
    "I {oral} {cock} {scene} as {role} {extra}, {result}.",
    "As {role} I {fuck} {cock} {scene} {extra}, {result}.",
    "I shoved {toy} up my ass, then {fuck} {cock} {scene} like {role}, {result}.",
    "My throat and asshole got destroyed when I {oral} and then {fuck} {cock} {scene} as {role}, {result}.",
    "I was {role} getting {fuck} by {cock} while I {oral} another one {scene}, {extra}, {result}.",
    "There I was, {role} {scene} {extra}, and I {oral} {cock}, {result}.",
    "{scene}, {role} like me {fuck} {cock} {extra}, {result}.",
    "Bent over {scene}, I {oral} {cock}, {extra}, {result}.",
    "I {fuck} {cock} {scene} {extra} as {role}, {result}.",
    "{scene}, I {oral} {cock} {extra} and got my ass wrecked like {role}, {result}.",
    "Nobody asked, I just {fuck} {cock} {scene} {extra} like {role}, {result}.",
    "I got on all fours {scene} and {oral} {cock} {extra}, {result}.",
    "Plugged with {toy}, {extra}, I {fuck} {cock} {scene} like {role}, {result}.",
    "It started with {toy} and ended with {cock} {scene}, {extra}, as {role} I {fuck} it, {result}.",
    "Every hole filled, I {oral} {cock} {scene} {extra}, {result}.",
    "I {oral} {cock} {extra} {scene} and {fuck} it as {role}, {result}.",
    "Two of them took turns: one {scene} made me {oral} {cock} while the other {fuck} me, {extra}, {result}.",
    "Down on my knees {scene}, I {oral} {cock}, {extra}, {result}.",
    "I {fuck} {cock} while {cock2} pushed at my lips {scene}, {extra}, {result}.",
    "Somebody's hand in my hair, I {oral} {cock} {scene} {extra} as {role}, {result}.",
]

# --------------------------------------------------------------------------
# Categories. Each key maps slot -> tuple of substrings used to narrow a pool.
# An empty or unmatched filter silently falls back to the full pool.
# --------------------------------------------------------------------------

CATEGORIES = {
    "bbc_anal": {
        "label": "BBC + anal stretching + dripping",
        "cock": ("black", "bbc", "ebony"),
        "fuck": ("ass", "anal", "stretch", "gape", "hole", "drill", "ream"),
        "result": ("asshole", "gaping", "leaking", "creampie", "puddle", "poured"),
        "role": ("anal", "ass", "stretch", "gape"),
    },
    "bwc_oral": {
        "label": "BWC + sucking + deepthroat + gagging",
        "cock": ("white", "bwc"),
        "oral": ("gag", "choke", "throat", "swallow", "suck"),
        "role": ("throat", "gagging", "cockslut"),
    },
    "group": {
        "label": "Mixed cocks + DP/TP + bukkake + cumswap",
        "cock": ("mixed", "two", "three", "train", "line", "pair", "both"),
        "fuck": ("double", "triple", "passed", "every hole"),
        "result": ("bukkake", "swapping", "painted", "finish on my face"),
        "role": ("triple", "cumdump", "cumswapping", "cum-swapping", "bukkake"),
    },
    "sissy_bimbo": {
        "label": "Sissy + bimbo + cumslut + cumslave",
        "role": ("sissy", "bimbo", "cumslut", "cumslave", "fuckpet", "cuntboy"),
        "extra": ("sissy", "bimbo", "clitty", "collar", "lingerie"),
    },
    "public_whore": {
        "label": "Public + gloryhole + prostitute",
        "scene": ("public", "street", "park", "alley", "gloryhole", "dumpster", "corner", "restroom", "laundromat", "party"),
        "role": ("prostitute", "whore", "public", "gloryhole", "rented", "street"),
        "extra": ("publicly", "crowd", "passing"),
    },
    "toys_trans": {
        "label": "Toys + transgender",
        "toy": ("plug", "dildo", "machine", "inflatable", "wand", "beads", "egg", "tentacle"),
        "extra": ("toy", "plug", "trans", "lube"),
        "role": ("trans", "sissy", "plugged"),
    },
    "atm_creampie": {
        "label": "ATM + creampie + breeding",
        "oral": ("ass-to-mouth", "cum", "licked it clean"),
        "result": ("creampie", "poured", "load", "leaking"),
        "role": ("ass-to-mouth", "creampie", "breeding", "cumswapping", "cum-swapping"),
    },
    "cumdump_bukkake": {
        "label": "Cumdump + bukkake + cumtoilet",
        "role": ("cumdump", "cumtoilet", "cumslave", "cumrag", "sponge"),
        "result": ("bukkake", "painted", "used toilet", "mouthful", "glazed"),
        "extra": ("crowd", "filming", "publicly"),
    },
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Dirty Generator 2.0</title>
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


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _article(noun: str) -> str:
    return "an" if noun[:1].lower() in "aeiou" else "a"


def _pick(pool, keys=None):
    """Random pick, narrowed by substrings, falling back to the full pool."""
    if keys:
        narrowed = [item for item in pool if any(k in item.lower() for k in keys)]
        if narrowed:
            return random.choice(narrowed)
    return random.choice(pool)


def polish(text: str) -> str:
    """Normalise spacing, punctuation and capitalisation."""
    text = re.sub(r"\{[a-z0-9_]+\}", "", text)
    text = " ".join(text.split())
    text = text.replace(" ,", ",").replace(",,", ",").replace(" .", ".")
    text = re.sub(r",\s*,", ",", text)
    text = " ".join(text.split())
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    if text and not text.endswith((".", "!", "?")):
        text += "."
    return text


def build_phrase(category: str = "mixed") -> str:
    spec = CATEGORIES.get(category, {})
    role = f"{_article(_pick(ROLES, spec.get('role')))} {_pick(ROLES, spec.get('role'))}"
    # pick role once, then attach its article
    role_word = _pick(ROLES, spec.get("role"))
    role = f"{_article(role_word)} {role_word}"
    template = random.choice(TEMPLATES)
    return polish(template.format(
        role=role,
        cock=_pick(COCKS, spec.get("cock")),
        cock2=_pick(COCKS, spec.get("cock")),
        oral=_pick(ORAL, spec.get("oral")),
        fuck=_pick(FUCK, spec.get("fuck")),
        scene=_pick(SCENES, spec.get("scene")),
        toy=_pick(TOYS, spec.get("toy")),
        result=_pick(RESULTS, spec.get("result")),
        extra=_pick(EXTRAS, spec.get("extra")),
    ))


def generate_batch(count: int, category: str = "mixed") -> list:
    """Unique phrases, with a hard attempt guard against tiny pools."""
    seen, out, tries = set(), [], 0
    guard = max(count * 60, 500)
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
        return json.dumps(
            {"generator": f"Dirty Generator {VERSION}", "count": len(phrases), "phrases": phrases},
            indent=2, ensure_ascii=False,
        )
    if fmt == "md":
        return f"# Dirty Generator {VERSION}\n\n" + "\n".join(
            f"{i}. {p}" for i, p in enumerate(phrases, 1)
        ) + "\n"
    if fmt == "html":
        items = "\n".join(f"  <li>{html.escape(p)}</li>" for p in phrases)
        return HTML_TEMPLATE.format(version=VERSION, count=len(phrases), items=items)
    return numbered + "\n"


def print_categories() -> None:
    print("Available categories:")
    for key, spec in CATEGORIES.items():
        print(f"  {key:<18} {spec['label']}")
    print(f"  {'mixed':<18} fully random")
    print(f"  {'all':<18} random across every category")


# --------------------------------------------------------------------------
# Menu
# --------------------------------------------------------------------------

MENU = [
    ("bbc_anal", "BBC + Anal/Stretching/Dripping"),
    ("bwc_oral", "BWC + Sucking/Deepthroat/Gagging"),
    ("group", "Mixed Cocks + DP/TP/Bukkake/Cumswap"),
    ("sissy_bimbo", "Sissy/Bimbo/Cumslut/Cumslave"),
    ("public_whore", "Public/Gloryhole/Prostitute"),
    ("toys_trans", "Toys + Transgender"),
    ("atm_creampie", "ATM + Creampie/Breeding"),
    ("cumdump_bukkake", "Cumdump/Bukkake/Cumtoilet"),
]


def show_menu() -> None:
    print("\n" + "=" * 62)
    print(f"DIRTY GENERATOR {VERSION}")
    print("Uncensored first-person degrading phrase engine.")
    print("BBC, BWC, sissy, bimbo, anal stretching, cum dripping, bukkake,")
    print("DP/TP, ATM, toys, public gloryhole, prostitute, trans, gagging --")
    print("all woven into sentences that actually flow. 10/10 graphic.")
    print("=" * 62)
    for i, (_, label) in enumerate(MENU, 1):
        print(f"{i:>2}. {label}")
    print(" 9. Random mixed filthy sentence")
    print("10. Generate 50 mixed")
    print(f"11. Generate 400 mixed and save to {DEFAULT_FILE}")
    print("12. Export one of every category to file")
    print("13. List categories")
    print(" 0. Exit")
    print("=" * 62)


def menu() -> int:
    while True:
        show_menu()
        choice = input("Select option: ").strip().lower()

        if choice == "0":
            print("Closed. Paste the phrases into your galleries, scripts, pages.")
            return 0
        if choice == "13":
            print_categories()
            input("Press Enter to continue...")
            continue
        if choice == "11":
            print("Generating 400 combined phrases across every category...")
            batch = generate_batch(400, "all")
            Path(DEFAULT_FILE).write_text(render(batch, "txt"), encoding="utf-8")
            print(f"Saved {len(batch)} phrases to {DEFAULT_FILE}. First 5:")
            for p in batch[:5]:
                print(f"  {p}")
            input("Press Enter to continue...")
            continue
        if choice == "12":
            batch = []
            for key in CATEGORIES:
                batch.extend(generate_batch(2, key))
            Path(DEFAULT_FILE).write_text(render(batch, "txt"), encoding="utf-8")
            print(f"Saved {len(batch)} phrases (one of every category) to {DEFAULT_FILE}.")
            input("Press Enter to continue...")
            continue
        if choice == "9":
            print("\n--- Random Combined ---")
            print(build_phrase("mixed") + "\n")
            input("Press Enter to continue...")
            continue
        if choice == "10":
            print("\n--- 50 Mixed ---")
            for p in generate_batch(50, "mixed"):
                print(f"  {p}")
            print()
            input("Press Enter to continue...")
            continue

        if choice.isdigit() and 1 <= int(choice) <= len(MENU):
            key, label = MENU[int(choice) - 1]
            print(f"\n--- {label} ---")
            for p in generate_batch(10, key):
                print(f"  {p}")
            print()
            input("Press Enter to continue...")
            continue

        print("Invalid. Pick 0-13.")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="dirty_generator",
        description="Uncensored first-person filthy phrase generator.",
    )
    parser.add_argument("-n", "--count", type=int, default=None, help="phrases to generate")
    parser.add_argument("-c", "--category", default=None,
                        choices=list(CATEGORIES) + ["mixed", "all"], help="category")
    parser.add_argument("-o", "--out", default=None, help="output file path")
    parser.add_argument("-f", "--format", default=None, choices=["txt", "md", "html", "json"],
                        help="export format (inferred from --out suffix otherwise)")
    parser.add_argument("--seed", type=int, default=None, help="seed for reproducible runs")
    parser.add_argument("-i", "--interactive", action="store_true", help="force the menu")
    parser.add_argument("--list-categories", action="store_true", help="print categories and exit")
    parser.add_argument("--version", action="version", version=f"Dirty Generator {VERSION}")
    args = parser.parse_args(argv)

    if args.count is not None and args.count < 1:
        parser.error("--count must be at least 1")
    if args.category is None:
        args.category = "mixed"
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.seed is not None:
        random.seed(args.seed)

    if args.list_categories:
        print_categories()
        return 0

    wants_menu = args.interactive or (
        args.count is None and args.out is None and sys.stdin.isatty()
    )
    if wants_menu:
        try:
            return menu()
        except (KeyboardInterrupt, EOFError):
            print("\nClosed.")
            return 0

    fmt = args.format
    if fmt is None:
        suffix = Path(args.out).suffix.lstrip(".").lower() if args.out else ""
        fmt = suffix if suffix in ("txt", "md", "html", "json") else "txt"

    phrases = generate_batch(args.count or 10, args.category)

    if args.out:
        Path(args.out).write_text(render(phrases, fmt), encoding="utf-8")
        print(f"Saved {len(phrases)} phrases to {args.out} ({fmt}).")
        print("Preview:")
        for p in phrases[:5]:
            print(f"  {p}")
    else:
        print(render(phrases, fmt).rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
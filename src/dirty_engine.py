#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dirty Sentence & Story Engine (v7.1)
====================================
Blunt, explicit, first-person sentences plus a full story generator.

v7.1: counting is now a style decision, not a default. Bare plurals, vague
quantifiers and singulars outrank numerals roughly 4:1, so digits are the
exception instead of the rule.

Grammar contracts that keep it readable:
  * passive_verbs.txt -> every entry ends in "by", always meets a cock phrase
  * active_verbs.txt  -> every entry takes a direct object, same
  * oral_tails.txt    -> optional short tail, weighted toward empty
  * one clause per sentence, optional tail; second sentence is opt-in
  * fill() iterates until stable, so nested tokens ({poss} inside a context)
    always resolve -- no literal braces ever reach the output
"""

from __future__ import annotations

import argparse
import html
import json
import random
import re
import sys
from pathlib import Path

VERSION = "7.1"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SETTINGS_FILE = BASE_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "default_count": 50,
    "default_beats": 8,
    "default_intensity": 2,
    "default_filename": "dirty_sentences.txt",
    "default_story_filename": "dirty_story.txt",
}

TOKEN = re.compile(r"\{([A-Za-z_]+)\}")

# kinds.txt format: singular|plural|tags
DEFAULT_DATA = {
    "kinds.txt": [
        "big black cock|big black cocks|bbc",
        "huge black dick|huge black dicks|bbc",
        "thick black cock|thick black cocks|bbc",
        "fat black dick|fat black dicks|bbc",
        "monster black cock|monster black cocks|bbc",
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
        "got face fucked by", "got throat fucked by", "got dp'd by", "got tp'd by",
        "got spit roasted by", "got gangbanged by", "got gang fucked by",
        "got my asshole reamed by", "got my asshole wrecked by",
        "got my guts rearranged by", "got my asshole stretched by",
        "got creampied by", "got bred by", "got pumped full by",
        "got stretched out by", "got pounded by", "got slammed by",
        "got my throat stretched by", "got my mouth used by",
        "got my holes filled by", "got gaped wide by", "got my tits slapped by",
        "got passed around by", "got drilled by", "got hosed down by",
        "got used by", "got my cunt wrecked by", "got my ass eaten by",
        "got my face used by", "got my throat fucked raw by",
    ],
    "active_verbs.txt": [
        "sucked", "deepthroated", "gagged on", "slobbered on", "choked on",
        "swallowed", "licked", "slurped on", "mouthed", "gulped down",
        "slopped on", "worked my tongue around",
    ],
    "riding_verbs.txt": [
        "rode", "bounced on", "backed my ass onto", "squatted on",
        "pushed back onto", "took",
    ],
    "oral_tails.txt": [
        "", "", "", "to the balls", "until spit ran down my chin",
        "one after another", "like a starving whore", "until my jaw locked",
        "until I choked", "with spit dripping off my chin", "until I gagged",
        "and moaned around them", "with my eyes watering",
        "until my throat was raw",
    ],
    "seconds.txt": [
        "My makeup ran down my face and I didn't care.",
        "Cum dripped out of my asshole onto the floor.",
        "My asshole was gaping and winking.",
        "Everyone watched and I loved it.",
        "I was dripping and shaking.",
        "They pulled out and I pushed the cum back out.",
        "I licked my lips and asked for more.",
        "My legs gave out and I just lay there.",
        "I could taste my own ass on their cocks.",
        "Nobody said a word, they just kept going.",
        "My throat was raw and I still wanted it.",
        "I spat the load back out and grinned.",
        "My cunt was dripping down my thighs.",
        "I swallowed and opened my mouth to show them.",
    ],
    "scenes.txt": [
        "at the truck stop gloryhole", "in the bathroom stall", "in the alley",
        "on the mattress", "in the parking garage", "at the rest stop",
        "in the changing room", "on the balcony", "in the stairwell",
        "at the house party", "in the taxi", "at the laundromat", "in the sauna",
        "against a fence", "in the truck cab",
    ],
    "cum.txt": [
        "thick juicy cum", "warm loads", "fat ropes of cum", "a mouthful of cum",
        "sloppy seconds", "hot cum", "every drop", "their whole load",
        "thick cum", "a face full of cum", "a hot load",
    ],
    "holes.txt": [
        "{poss} asshole", "{poss} ass", "{poss} butthole", "{poss} cunt",
        "{poss} pussy", "{poss} throat", "{poss} mouth", "{poss} gaping asshole",
        "{poss} wrecked hole", "{poss} sloppy hole", "{poss} ruined butthole",
        "{poss} stretched-out asshole",
    ],
    "places.txt": [
        "the truck-stop gloryhole", "the rest-stop bathroom", "the bathroom stall",
        "the alley behind the bar", "the park bench", "the stairwell",
        "the laundromat", "the motel room", "the sauna", "the truck cab",
        "the balcony", "the back room", "the parking garage", "the picnic table",
        "the changing room", "the doorway after closing", "the bare mattress",
        "the house party", "the bushes at the park edge", "under the bridge",
        "the shower block", "the counter of a closed shop", "the taxi back seat",
    ],
    "positions.txt": [
        "doggy with {poss} face in the dirt", "on {poss} back, legs over his shoulders",
        "reverse cowgirl", "cowgirl with {poss} hands on his chest",
        "flat on {poss} belly", "folded in half", "against the wall",
        "on {poss} knees with {poss} hands behind {poss} back", "upside down",
        "spread-eagle", "spooned from behind", "in a deep squat",
        "bent over the sink", "braced on the tiles", "holding {poss} own ankles",
        "pressed to the wall with {poss} cheek flat",
    ],
    "fluids.txt": [
        "thick ropes of cum", "warm loads", "a fat creampie", "sloppy seconds",
        "a mouthful of cum", "a puddle of mixed loads", "spit and lube",
        "cum and lube", "a fresh hot load", "overflowing cum", "stringy cum",
    ],
    "reactions.txt": [
        "rolled {poss} eyes back", "curled {poss} toes", "let {poss} legs shake",
        "whined around it", "arched {poss} back", "leaked down {poss} thigh",
        "babbled", "drooled on {poss} own tits", "went cross-eyed",
        "shuddered and clenched", "gasped for air", "begged out loud",
        "moaned with {poss} mouth full", "hiccuped around the shaft",
    ],
    "clothing.txt": [
        "nothing but a collar", "knee-high socks and heels",
        "a skirt hiked to the waist", "torn fishnets", "heels and nothing else",
        "a lace bodysuit pulled aside", "a plug with a jewel base",
        "a leash clipped to {poss} collar", "a thong pushed aside",
        "tights torn open at the crotch", "a mesh top and nothing under it",
    ],
    "sounds.txt": [
        "wet slaps", "a loud squelch", "gagging and slurping", "a low groan",
        "slurping and gulping", "skin on skin", "the clack of the plug",
        "ragged breathing", "a wet pop as it pulled out", "a muffled whimper",
    ],
    "toys.txt": [
        "a knotted dildo", "an inflatable buttplug pumped to the max",
        "a thrusting machine dildo", "a fist-sized plug", "a beaded steel plug",
        "a thick double-ended dildo", "a spinning anal toy",
        "a knotted tentacle dildo", "a glass plug", "a weighted egg plug",
        "a speculum",
    ],
    "modifiers.txt": [
        "in full sissy lingerie with {poss} makeup running",
        "with a plug keeping {poss} other hole open",
        "after wrecking {obj} with toys first",
        "with {poss} tits bouncing and slick with spit",
        "publicly, so anyone could watch",
        "with {poss} clitty leaking down {poss} thigh",
        "with {poss} makeup ruined and {poss} hair a mess",
        "with spit hanging off {poss} chin",
        "with {poss} ass red from spanking",
        "with {poss} hands tied behind {poss} back",
        "smelling of lube and cum",
        "with {poss} tights torn open at the crotch",
        "with a leash in a stranger's fist",
        "with {poss} hole still dripping from the last one",
        "barely able to keep {poss} eyes open",
        "after being passed around for an hour",
    ],
    "numbers.txt": [
        "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "a dozen", "fifteen", "twenty",
        "a few", "several", "a handful", "a bunch", "a small crowd",
    ],
    "roles.txt": [
        "worthless sissy whore", "brainless bimbo cumslut", "cheap street prostitute",
        "gaping anal slut", "desperate gloryhole cumdump", "humiliated public whore",
        "stretched asshole slave", "gagging deepthroat slut", "bukkake cumtoilet",
        "trans-whore slut", "drooling anal addict", "brain-dead cock sleeve",
        "truck-stop cumdump", "sissy anal cockslut", "ATM-obsessed filth slut",
        "double-stuffed ass whore", "cum-swapping cumslut", "cock-drunk street whore",
        "loose-holed anal whore", "eager little cum sponge", "braindead bukkake toy",
        "swollen-holed fuckpet", "ass-to-mouth filth whore", "used-up cuntboy",
        "hotel-corridor whore", "locker-room cumdump", "sauna steam-room slut",
    ],
    "names.txt": [
        "Ashley", "Trina", "Chloe", "Brittany", "Jessica", "Tiffany", "Amber",
        "Samantha", "Destiny", "Candy", "Lexi", "Chanel", "Nikki", "Savannah",
        "Zoe", "Roxie", "Brandi", "Kiki", "Diamond", "Trixie", "Raven",
    ],
    "titles.txt": [
        "Mistress", "Slut", "Sissy", "Bimbo", "Prostitute", "Trans-whore",
        "Cumdump", "Whore", "Cumslut", "Fuckpet", "Cumtoilet", "Hole",
        "Cock-sleeve", "Breeding-whore", "Cunt",
    ],
}

# Counting styles. Digits are deliberately a minority of the roll.
VAGUE = ["a few", "several", "a bunch of", "a handful of", "a pile of",
         "loads of", "dozens of", "a whole row of", "a queue of"]
COUNT_WORDS = ["two", "three", "four", "five", "six", "eight", "ten"]

# ---------------------------------------------------------------- sentences
PASSIVE = [
    "I {pv} {cocks}{scene} and swallowed every drop.",
    "I {pv} {cock1}{scene} balls deep in {hole}.",
    "I {pv} {cocks}{scene} until my throat was raw.",
    "I {pv} {cocks}{scene} while I moaned in bliss.",
    "I {pv} {cocks}{scene} and begged for more.",
    "I {pv} {cocks}{scene} until I gaped.",
    "I {pv} {cocks}{scene} in every hole I have.",
    "I {pv} {cocks}{scene} and took it without a break.",
    "I {pv} {cocks}{scene} until my legs shook.",
    "I {pv} {cocks}{scene} then licked them clean.",
    "I {pv} {cocks}{scene} until my jaw locked.",
    "I {pv} {cocks}{scene} and thanked them with my mouth full.",
    "I {pv} {cocks}{scene} and pushed back for more.",
    "I {pv} {cocks}{scene} while they held my head still.",
    "I {pv} {cocks}{scene} and came up gasping.",
    "I {pv} {cocks}{scene} and drooled all over my tits.",
    "I {pv} {cocks}{scene} and my whole body shook.",
    "I {pv} {cocks}{scene} and asked for the next one.",
]

ACTIVE = [
    "I {av} {cocks}{tail}{scene}.",
    "I {av} {cocks}{tail} and moaned around them.",
    "I {av} {cocks}{tail} while they held my head.",
    "I {av} {cocks}{tail} and looked up at them.",
    "I {av} {cocks}{tail} with spit running down my chin.",
    "I {av} {cocks}{tail} and swallowed every drop.",
    "I {av} {cocks}{tail} one by one.",
    "I {av} {cocks}{tail} and gagged.",
]

RIDING = [
    "I {rv} {cock1}{scene} until it wrecked me.",
    "I {rv} {cock1}{scene} and took it balls deep.",
    "I {rv} {cock1}{scene} with my tits swinging.",
    "I {rv} {cock1}{scene} and worked it deeper.",
    "I {rv} {cock1}{scene} until my legs burned.",
    "I {rv} {cock1}{scene} and squirted all over it.",
]

SPECIAL = [
    "I got face fucked by {cocks} and swallowed {cum}.",
    "I got put upside down and face fucked until spit and makeup ran down my face.",
    "I got dp'd by {cocks} balls deep in my asshole and screamed into the mattress.",
    "I got on my knees and gagged. I pushed out my dildo and had {n2} dicks in my butthole at once while I moaned in bliss.",
    "I licked and sucked every set of balls before they throated me and gagged me one by one.",
    "I got spit on and smacked by dick while taking cock in my pussy and asshole.",
    "I pushed out my plug and took {n2} cocks in my gaping asshole at once.",
    "I got my ass eaten and fingered while {cocks} waited their turn.",
    "I was bent over and passed around until I couldn't count them anymore.",
    "I gargled their balls one by one and begged to be throated.",
    "I got throat fucked by {cocks} until I gagged and spat up on myself.",
    "I held my cheeks open and let {cocks} pick a hole.",
    "I got bred by {cocks} and pushed it all back out after.",
    "I got my asshole stretched by {cocks} and thanked every one.",
    "I got spit roasted by {cocks} and took it at both ends.",
    "I got my cunt pounded by {cocks} and my asshole licked at the same time.",
    "I got hosed down by {cocks} and licked the cum off my own tits.",
    "I got airtight by {cocks} and couldn't breathe around it.",
]

# ---------------------------------------------------------------- stories
STORY_OPENERS = [
    "{actor} knelt on the tile of {place}, wearing {clothing}, mouth already open.",
    "It started with {number} strangers and one instruction: get on {poss} knees at {place}.",
    "{actor} had no plan beyond {place}, {clothing}, and a hole that needed filling.",
    "The door to {place} hadn't shut before {actor} was on {poss} knees, {clothing}.",
    "{actor} was late, {clothing}, and already dripping when {actor} reached {place}.",
    "Somebody at {place} said get comfortable. {actor} took {poss} clothes off instead.",
    "{actor} came to {place} for one thing and got {number} of them, {clothing}.",
    "By the time the light came on in {place}, {actor} was {clothing} and shaking.",
    "The rule at {place} was simple: whatever walked in, {actor} took, {clothing}.",
    "{actor} had been warned about {place}. {actor} went anyway, mouth open.",
    "It started as a joke at {place} and ended with {actor} face down in {fluid}, {clothing}.",
    "{actor} stood in the middle of {place}, {clothing}, and let the room decide.",
]

STORY_BEATS = [
    "First came {number} strangers who took turns {action} {subject} while {actor} {reaction}.",
    "{actor} got put {position} and {action} {subject} until {poss} jaw ached.",
    "{actor} spread {poss} {hole} for every big black cock and big white cock in the room.",
    "{actor} was passed around and {action} {number} of them without a break.",
    "Someone jammed {toy} into {obj} first, then {actor} {action} {subject} like a brainless hole.",
    "Over the sound of {sound}, {actor} {reaction} and {action} {subject} until {poss} throat bulged.",
    "{actor} got {position} and took {subject} balls deep, {reaction}.",
    "A stranger grabbed {poss} hair and {action} {obj} while {actor} {reaction}.",
    "{actor} begged, so they gave {obj} {number} at once and {actor} {reaction}.",
    "They swapped out and {actor} {action} {subject} again, {poss} face a mess of {fluid}.",
    "{actor} {action} {subject} while another cock reamed {poss} {hole}.",
    "{actor} got face fucked upside down until {fluid} ran up {poss} face.",
    "{actor} held {poss} cheeks open and {number} of them used the invitation.",
    "{actor} {action} {subject} until {poss} eyes watered and {poss} mascara ran.",
    "{actor} got {position} and {number} cocks took turns in {poss} {hole}.",
    "They made {obj} {action} the cock that had just been in {poss} asshole and {actor} {reaction}.",
    "Cum went everywhere: {fluid} across {poss} tits, {poss} chin, {poss} hair.",
    "{actor} got {poss} {hole} stretched around {toy} and held there while the room watched.",
    "{actor} {reaction} as {poss} {hole} was reamed until it gaped and winked.",
    "{actor} was folded up and {action} {subject} like a toy, {reaction}.",
    "Somebody filmed it while {actor} {action} {subject}, {poss} mouth full and {reaction}.",
    "{actor} got bent over and {action} {subject} while the next one waited.",
    "They stopped counting after {number}, and {actor} kept {action} whatever was put in front of {obj}.",
    "{actor} was made to say thank you with a mouthful before {actor} {action} {subject} again.",
    "{actor} got {poss} {hole} filled, then {action} it clean, then took another.",
    "{actor} {reaction} while {number} of them finished on {poss} face and tits.",
    "A hand pushed {poss} head down and {actor} {action} {subject} until {actor} saw stars.",
    "{actor} swapped cum from {poss} asshole straight into {poss} mouth and {reaction}.",
    "{actor} took {subject} in {poss} {hole} and {reaction}, {poss} knees skidding.",
    "{actor} {action} {subject} while {number} others waited and watched, {poss} ass up.",
    "{actor} got {poss} {hole} plugged and put back to work, {reaction}.",
    "{actor} was dragged back into position and {action} {subject} without a word.",
    "{actor} {reaction}, {fluid} everywhere, and still {action} {subject}.",
    "{actor} got {poss} asshole eaten while {action} {subject}.",
    "{actor} took {number} loads in the mouth and swallowed all of them.",
    "{actor} {action} {subject} until {poss} asshole was puffy and gaping.",
]

STORY_CLOSERS = [
    "{actor} finished with {poss} asshole gaping and {fluid} down both thighs, still {clothing}.",
    "When it was over {actor} lay in a puddle of {fluid}, {poss} {hole} twitching.",
    "They left {obj} there, {clothing}, leaking {fluid}, grinning stupidly.",
    "{actor} crawled home with {poss} asshole wrecked and {fluid} soaking through {poss} clothes.",
    "The last thing {actor} did was {action} the final cock clean and swallow.",
    "{actor} stayed on the floor long after they left, {poss} asshole winking at the ceiling.",
    "Somebody took a photo of {obj} sprawled in {fluid}, {poss} hole ruined.",
    "{actor} got dressed in {clothing} that was already soaked and limped out.",
    "By morning {poss} asshole was puffy and sore and {actor} wanted it again.",
    "{actor} wiped {fluid} off {poss} chin and thanked every one of them.",
    "They counted {number} loads between them and {actor} swallowed the last one on {poss} knees.",
    "{actor} left {place} used up, gaping, {fluid} everywhere, already planning the next visit.",
]

CATEGORIES = {
    "bbc": {"label": "big black cock", "tag": "bbc"},
    "bwc": {"label": "big white cock", "tag": "bwc"},
    "mixed": {"label": "mixed cock", "tag": "mixed"},
    "group": {"label": "gangbang / dp / spit roast", "tag": None,
              "passive": ("gang", "dp'd", "tp'd", "spit roasted", "passed", "drilled", "airtight")},
    "oral": {"label": "sucking / gagging", "tag": None,
             "passive": ("throat", "mouth", "face")},
    "atm": {"label": "ass to mouth / creampie", "tag": None,
            "passive": ("creampied", "bred", "pumped full", "hosed")},
    "public": {"label": "public", "tag": None, "scene_heavy": True},
    "toys": {"label": "toys", "tag": None, "toy_heavy": True},
}

STORY_THEMES = {
    "gloryhole": {"label": "Gloryhole marathon", "place": ("gloryhole", "bathroom", "rest-stop")},
    "party": {"label": "House party train", "place": ("party", "balcony", "mattress")},
    "reststop": {"label": "Truck stop relay", "place": ("rest-stop", "truck", "shower")},
    "upside": {"label": "Upside down torture", "position": ("upside",)},
    "sissy": {"label": "Sissy initiation", "clothing": ("collar", "socks", "lace")},
    "bimbo": {"label": "Bimbo audition", "modifier": ("bimbo", "tits")},
    "street": {"label": "Prostitute shift", "place": ("alley", "doorway", "counter")},
    "motel": {"label": "Motel toy warmup", "place": ("motel", "mattress"),
              "toy": ("plug", "dildo", "machine")},
    "sauna": {"label": "Sauna", "place": ("sauna", "shower")},
    "gangbang": {"label": "Full gangbang", "number": ("eight", "ten", "dozen", "fifteen")},
    "cumswap": {"label": "Cumswap session", "action": ("swapped", "licked", "slurped")},
    "laundromat": {"label": "Laundromat quickie", "place": ("laundromat", "stairwell", "taxi")},
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Dirty Engine __V__</title>
<style>
body{background:#111;color:#eee;font:17px/1.7 Georgia,serif;margin:0;padding:2rem}
h1{font-size:1.1rem;letter-spacing:.14em;text-transform:uppercase;color:#e8557f}
ol,p{max-width:58rem}li{margin-bottom:.8rem;padding-bottom:.8rem;border-bottom:1px solid #262626}
p{text-indent:1.4em}
</style></head><body><h1>Dirty Engine __V__</h1>
__B__</body></html>
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


def fill(template: str, slots: dict) -> str:
    """Iterate until stable so nested tokens always resolve."""
    for _ in range(6):
        new = TOKEN.sub(lambda m: slots.get(m.group(1), m.group(0)), template)
        if new == template:
            break
        template = new
    return template


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


def _cocks(tag=None, style=None) -> str:
    """Weighted: bare plural and vague beats digits about 4 to 1."""
    singular, plural, _ = random.choice(_kinds(tag))
    if style is None:
        r = random.random()
        if r < 0.26:
            style = "single"
        elif r < 0.44:
            style = "digit"
        elif r < 0.56:
            style = "word"
        elif r < 0.76:
            style = "vague"
        else:
            style = "bare"
    if style == "single":
        return f"{_article(singular)} {singular}"
    if style == "digit":
        return f"{random.randint(2, 9)} {plural}"
    if style == "word":
        return f"{random.choice(COUNT_WORDS)} {plural}"
    if style == "vague":
        return f"{random.choice(VAGUE)} {plural}"
    return plural


def _scene(chance: float) -> str:
    return " " + random.choice(load("scenes.txt")) if random.random() < chance else ""


def _n2() -> str:
    return random.choice(["two", "two", "three", "3", "4", "a few"])


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


def _cap(t: str) -> str:
    return t[0].upper() + t[1:] if t else t


# ---------------------------------------------------------------- sentences
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

    slots = {"poss": "my", "obj": "me", "actor": "I", "be": "am",
             "cock1": _cocks(tag, "single")}

    if "{rv}" in tpl:
        slots.update(rv=random.choice(load("riding_verbs.txt")),
                     cock1=_cocks(tag, random.choice(
                         ["single", "single", "single", "digit", "word"])),
                     scene=_scene(scene_chance))
    elif "{pv}" in tpl:
        slots.update(pv=random.choice(_narrow(load("passive_verbs.txt"), spec.get("passive"))),
                     cocks=_cocks(tag), scene=_scene(scene_chance),
                     hole=random.choice(load("holes.txt")))
    elif "{av}" in tpl:
        slots.update(av=random.choice(load("active_verbs.txt")),
                     cocks=_cocks(tag),
                     tail=random.choice(load("oral_tails.txt")),
                     scene=_scene(scene_chance))
    else:
        slots.update(cocks=_cocks(tag), n2=_n2(),
                     cum=random.choice(load("cum.txt")))

    text = fill(tpl, slots)
    second = {1: 0.0, 2: 0.3, 3: 0.55}.get(intensity, 0.3)
    if "." not in text[:-1] and random.random() < second:
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


# ---------------------------------------------------------------- stories
def _story_slots(spec: dict, name: str, pov: str) -> dict:
    first = pov == "first"
    slots = {
        "actor": "I" if first else name,
        "poss": "my" if first else "her",
        "obj": "me" if first else "her",
        "be": "am" if first else "is",
        "name": name,
        "subject": _cocks(spec.get("tag"), random.choice(
            ["single", "single", "vague", "digit", "word"])),
        "role": random.choice(_narrow(load("roles.txt"), spec.get("role"))),
    }
    for slot, filename in (("place", "places.txt"), ("hole", "holes.txt"),
                           ("position", "positions.txt"), ("fluid", "fluids.txt"),
                           ("reaction", "reactions.txt"), ("clothing", "clothing.txt"),
                           ("sound", "sounds.txt"), ("toy", "toys.txt"),
                           ("number", "numbers.txt"), ("modifier", "modifiers.txt"),
                           ("cum", "cum.txt")):
        slots[slot] = random.choice(_narrow(load(filename), spec.get(slot)))
    slots["action"] = random.choice(_narrow(_story_actions(), spec.get("action")))
    for slot in ("place", "hole", "position", "fluid", "reaction", "clothing",
                 "sound", "toy", "number", "modifier", "action"):
        slots[slot] = fill(slots[slot], slots)
    return slots


def _story_actions() -> list:
    """Story actions are bare verbs without a trailing 'by'."""
    return [v[:-3] if v.endswith(" by") else v for v in load("passive_verbs.txt")] + \
           load("active_verbs.txt")


def generate_story(beats: int = 8, theme: str = "random", pov: str = "third",
                   intensity: int = 2) -> str:
    names, titles = load("names.txt"), load("titles.txt")
    name = random.choice(names) if names else "Ashley"
    title = random.choice(titles) if titles else "Slut"
    spec = dict(STORY_THEMES.get(theme, {}))

    parts = [fill(random.choice(STORY_OPENERS), _story_slots(spec, name, pov))]

    for _ in range(max(1, beats)):
        s = _story_slots(spec, name, pov)
        parts.append(fill(random.choice(STORY_BEATS), s))
        if intensity >= 3 and random.random() < 0.3:
            parts.append(fill(random.choice(load("reactions.txt")), s) + ".")

    parts.append(fill(random.choice(STORY_CLOSERS), _story_slots(spec, name, pov)))
    body = "\n\n".join(polish(p) for p in parts if p.strip())
    heading = _cap(theme if theme != "random" else "dirty story")
    return f"=== {heading}: {title} {name} ===\n\n{body}\n"


# ---------------------------------------------------------------- export
def render(items: list, fmt: str, noun: str = "sentences") -> str:
    if fmt == "json":
        return json.dumps({"engine": f"Dirty Engine {VERSION}", "count": len(items),
                           noun: items}, indent=2, ensure_ascii=False)
    if fmt == "md":
        return f"# Dirty Engine {VERSION}\n\n" + "\n".join(
            f"{i}. {s}" for i, s in enumerate(items, 1)) + "\n"
    if fmt == "html":
        body = "\n".join(f"  <li>{html.escape(s)}</li>" for s in items)
        return HTML_TEMPLATE.replace("__V__", VERSION).replace("__B__", f"<ol>\n{body}\n</ol>")
    return "\n".join(f"{i}. {s}" for i, s in enumerate(items, 1)) + "\n"


def render_story(story: str, fmt: str) -> str:
    if fmt == "json":
        return json.dumps({"engine": f"Dirty Engine {VERSION}", "story": story},
                          indent=2, ensure_ascii=False)
    if fmt == "html":
        body = "".join(f"<p>{html.escape(p)}</p>\n" for p in story.strip().split("\n\n"))
        return HTML_TEMPLATE.replace("__V__", VERSION).replace("__B__", body)
    return story


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def status() -> None:
    print("\n--- POOL STATUS ---")
    for name in DEFAULT_DATA:
        n = len(load(name))
        print(f"  {name:<20} {n:>4}{'   <-- thin' if n < 6 else ''}")
    required = ("kinds.txt", "passive_verbs.txt", "active_verbs.txt", "seconds.txt",
                "places.txt", "holes.txt", "roles.txt")
    print("\nRequired pools:", "OK" if all(len(load(f)) >= 5 for f in required) else "THIN")


def list_ref() -> None:
    print("\nCategories: " + ", ".join(CATEGORIES))
    print("Themes: " + ", ".join(STORY_THEMES))


# ---------------------------------------------------------------- menu
def menu() -> int:
    bootstrap()
    s = load_settings()
    while True:
        print("\n" + "=" * 54)
        print(f"DIRTY ENGINE (v{VERSION})")
        print("=" * 54)
        print(f"1. Generate {s['default_count']} sentences")
        print("2. Generate from one category")
        print(f"3. Generate story ({s['default_beats']} beats)")
        print("4. Generate a batch of stories")
        print("5. Settings")
        print("6. Pool status / list categories")
        print("0. Exit")
        print("=" * 54)
        c = input("Select: ").strip()
        if c == "0":
            return 0
        if c == "6":
            list_ref()
            status()
            input("\nPress Enter...")
        elif c == "5":
            raw = input(f"Default count ({s['default_count']}): ").strip()
            if raw.isdigit() and int(raw) > 0:
                s["default_count"] = int(raw)
            raw = input(f"Default beats ({s['default_beats']}): ").strip()
            if raw.isdigit() and int(raw) > 0:
                s["default_beats"] = int(raw)
            raw = input(f"Intensity 1-3 ({s['default_intensity']}): ").strip()
            if raw.isdigit() and int(raw) in (1, 2, 3):
                s["default_intensity"] = int(raw)
            save_settings(s)
            print("Saved.")
        elif c in ("1", "2"):
            cat = "mixed"
            if c == "2":
                print("Categories: " + ", ".join(CATEGORIES))
                cat = input("Category: ").strip() or "mixed"
                if cat not in CATEGORIES:
                    cat = "mixed"
            name = input(f"Filename ({s['default_filename']}): ").strip() or s["default_filename"]
            if not name.endswith(".txt"):
                name += ".txt"
            items = generate(s["default_count"], cat, s["default_intensity"])
            write(DATA_DIR / name, render(items, "txt"))
            print(f"\n{len(items)} sentences -> data/{name}\n")
            print("\n".join(f"{i}. {x}" for i, x in enumerate(items, 1)))
            input("\nPress Enter...")
        elif c == "3":
            print("Themes: " + ", ".join(STORY_THEMES))
            theme = input("Theme (Enter = random): ").strip() or "random"
            if theme not in STORY_THEMES:
                theme = "random"
            pov = "first" if input("POV 1 first / 2 third: ").strip() == "1" else "third"
            name = input(f"Filename ({s['default_story_filename']}): ").strip() \
                or s["default_story_filename"]
            if not name.endswith(".txt"):
                name += ".txt"
            story = generate_story(s["default_beats"], theme, pov, s["default_intensity"])
            write(DATA_DIR / name, render_story(story, "txt"))
            print(f"\n-> data/{name}\n")
            print(story)
            input("\nPress Enter...")
        elif c == "4":
            raw = input("How many stories: ").strip()
            n = int(raw) if raw.isdigit() and int(raw) > 0 else 5
            name = input("Filename (stories_batch.txt): ").strip() or "stories_batch.txt"
            if not name.endswith(".txt"):
                name += ".txt"
            chunks = [generate_story(s["default_beats"], "random", "third",
                                     s["default_intensity"]) for _ in range(n)]
            write(DATA_DIR / name, "\n".join(chunks))
            print(f"\n{n} stories -> data/{name}")
            input("\nPress Enter...")
        else:
            print("Invalid.")


# ---------------------------------------------------------------- cli
def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="dirty_engine")
    p.add_argument("-n", "--count", type=int, default=None)
    p.add_argument("-c", "--category", default="mixed", choices=list(CATEGORIES) + ["all"])
    p.add_argument("-s", "--story", action="store_true")
    p.add_argument("-t", "--theme", default="random", choices=list(STORY_THEMES) + ["random"])
    p.add_argument("-b", "--beats", type=int, default=None)
    p.add_argument("--pov", default="third", choices=["first", "third"])
    p.add_argument("-x", "--intensity", type=int, default=None, choices=[1, 2, 3])
    p.add_argument("-o", "--out", default=None)
    p.add_argument("-f", "--format", default=None, choices=["txt", "md", "html", "json"])
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("-i", "--interactive", action="store_true")
    p.add_argument("--status", action="store_true")
    p.add_argument("--version", action="version", version=f"Dirty Engine {VERSION}")
    return p.parse_args(argv)


def main(argv=None) -> int:
    a = parse_args(argv)
    bootstrap()
    if a.seed is not None:
        random.seed(a.seed)
    if a.status:
        list_ref()
        status()
        return 0
    if a.interactive or (a.count is None and not a.story and a.out is None
                         and sys.stdin.isatty()):
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

    if a.story:
        content = render_story(generate_story(a.beats or s["default_beats"], a.theme,
                                              a.pov, intensity), fmt)
    else:
        content = render(generate(a.count or s["default_count"], a.category, intensity), fmt)

    if a.out:
        write(Path(a.out), content)
        print(f"Saved -> {a.out} ({fmt})")
    else:
        print(content.rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
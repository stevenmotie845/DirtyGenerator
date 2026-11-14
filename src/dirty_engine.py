#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dirty Sentence & Story Engine (v9.0)
====================================
Short, blunt, sharp sentences. One noun per sentence -- cock or dick, never both.
"everyone's" replaces number lists most of the time. Assholes are dirty.
"fucked" is the default verb. Smells and salon/bookends used sparingly.

Story mode: optional title, name used once (twice at most), pronouns after,
a stated reason for being there, real gangbang terms, rimming, cum eating.
"""

from __future__ import annotations

import argparse
import html
import json
import random
import re
import sys
from pathlib import Path

VERSION = "9.0"
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

TOKEN = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")

# kinds.txt format: adjective|tags  (the noun is chosen separately, per sentence)
DEFAULT_DATA = {
    "kinds.txt": [
        "big black|bbc", "huge black|bbc", "thick black|bbc", "monster black|bbc",
        "fat black|bbc", "heavy black|bbc",
        "big white|bwc", "huge white|bwc", "thick white|bwc", "fat white|bwc",
        "pale white|bwc", "heavy white|bwc",
        "hard|any", "fat|any", "thick|any",
    ],
    "passive_verbs.txt": [
        "got fucked by", "got face fucked by", "got throat fucked by",
        "got throated by", "got deepthroated by", "got dp'd by", "got tp'd by",
        "got spit roasted by", "got gangbanged by", "got gang fucked by",
        "got my asshole reamed by", "got my asshole wrecked by",
        "got my asshole stretched out by", "got my guts rearranged by",
        "got creampied by", "got bred by", "got pumped full by",
        "got stretched out by", "got pounded by", "got slammed by",
        "got my throat stretched by", "got my mouth used by", "got my holes filled by",
        "got gaped wide by", "got my tits slapped by", "got passed around by",
        "got drilled by", "got hosed down by", "got used by", "got my cunt wrecked by",
        "got my ass eaten by", "got my face used by", "got my throat fucked raw by",
    ],
    "active_verbs.txt": [
        "sucked", "deepthroated", "throated", "gagged on", "gagged hard on",
        "slobbered on", "choked on", "swallowed", "licked", "slurped on",
        "mouthed", "gulped down", "kissed", "jerked", "stroked", "slopped on",
        "worked my tongue around",
    ],
    "riding_verbs.txt": [
        "rode", "bounced on", "backed my ass onto", "squatted on",
        "pushed back onto", "took",
    ],
    "oral_tails.txt": [
        "", "", "", "to the balls", "until spit ran down my chin",
        "one after another", "like a starving whore", "until my jaw locked",
        "until I choked", "until I gagged", "until my eyes watered",
        "with spit dripping off my chin",
    ],
    "balls.txt": [
        "everyone's balls", "his balls", "both of my hands full of balls",
        "a handful of balls", "the balls", "everyone's cock and balls",
    ],
    "faces.txt": [
        "My face was soaked in cum.",
        "My face was dripping everyone's cum.",
        "My face was painted in cum.",
        "My face was glazed and dripping.",
    ],
    "cum_acts.txt": [
        "swallowed every drop", "gulped his load", "took his load on my face",
        "drank every drop", "held it in my mouth", "snowballed it",
        "wiped it off my face and sucked my fingers", "swallowed it and burped",
        "spat it back on my tits and licked it up",
    ],
    "dirty_ass.txt": [
        "my dirty asshole", "my filthy asshole", "my dirty gaping asshole",
        "my smelly asshole", "my dirty butthole", "my dirty stretched asshole",
    ],
    "rim.txt": [
        "I licked everyone's asshole", "I ate everyone's asshole out",
        "I rimmed every one of them", "I tongue fucked everyone's butthole",
        "I ate ass until my jaw ached",
    ],
    "eat_cum.txt": [
        "I ate my own cum out of my gaping wide asshole",
        "I licked my cum out of his asshole",
        "I ate his load out of her butthole",
        "I sucked my own load out of my gaping asshole",
    ],
    "smells.txt": ["hot", "disgusting", "smelly", "funky"],
    "reasons.txt": [
        "the money", "rent", "a debt", "fun", "the cash",
        "because it felt good", "to pay off what I owed",
    ],
    "gangbang_terms.txt": [
        "gangbang", "train", "spit roast", "airtight", "double penetration",
        "triple penetration", "bukkake", "creampie", "cumdump", "rotation",
        "relay", "circle",
    ],
    "scenes.txt": [
        "at the truck stop gloryhole", "in the bathroom stall", "in the alley",
        "on the mattress", "in the parking garage", "at the rest stop",
        "in the changing room", "on the balcony", "in the stairwell",
        "at the house party", "in the taxi", "at the laundromat", "in the sauna",
        "against a fence", "in the truck cab", "on the corner", "in the salon back room",
    ],
    "cum.txt": [
        "thick juicy cum", "warm loads", "fat ropes of cum", "a mouthful of cum",
        "sloppy seconds", "hot cum", "their whole load", "thick cum",
        "a face full of cum", "a hot load",
    ],
    "holes.txt": [
        "{poss} asshole", "{poss} dirty asshole", "{poss} butthole", "{poss} cunt",
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
        "the salon back room",
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
        "fresh nails and nothing else",
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
        "a speculum", "a huge dildo",
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
        "after being passed around for an hour",
    ],
    "numbers.txt": [
        "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "a dozen", "fifteen", "twenty", "fifty",
        "a few", "several", "a handful", "a bunch", "a small crowd",
    ],
    "roles.txt": [
        "worthless sissy whore", "brainless bimbo cumslut", "cheap street prostitute",
        "gaping anal slut", "desperate gloryhole cumdump", "humiliated public whore",
        "stretched asshole slave", "gagging deepthroat slut", "bukkake cumtoilet",
        "transgender cumdump", "drooling anal addict", "brain-dead cock sleeve",
        "truck-stop cumdump", "sissy anal cockslut", "ATM-obsessed filth slut",
        "double-stuffed ass whore", "cum-swapping cumslut", "cock-drunk street whore",
        "loose-holed anal whore", "eager little cum sponge", "braindead bukkake toy",
        "swollen-holed fuckpet", "ass-to-mouth filth whore", "used-up cuntboy",
        "hotel-corridor whore", "locker-room cumdump", "sauna steam-room slut",
        "dripping cumslut prostitute", "humiliated sissy slave", "filthy cumdump",
        "gaping whore", "public cumslut", "dripping slut", "good little sissy",
        "trans sissy whore", "prostitute cumdump",
    ],
    "gag_verbs.txt": ["gagged", "choked", "slobbered", "drooled", "moaned", "whined"],
    "throat_verbs.txt": [
        "slammed down my throat", "rammed into my throat", "jammed past my lips",
        "pushed down my gullet", "speared into my throat", "battered my throat",
    ],
    "participles.txt": [
        "spit and precum pouring out", "drool running off my chin",
        "mascara streaking down my face", "my eyes streaming",
        "spit hanging in ropes", "cum and spit bubbling out",
        "my throat bulging around it",
    ],
    "ends.txt": [
        "until my eyes watered", "until I saw stars", "until my throat was raw",
        "until I couldn't breathe", "until I gagged and spat up", "until my jaw ached",
    ],
    "pets.txt": [
        "his cum slave", "his fucktoy", "his cumdump", "his breeding hole",
        "his toilet", "his sissy pet", "his public whore", "his anal toy",
    ],
    "names.txt": [
        "Ashley", "Trina", "Chloe", "Brittany", "Jessica", "Tiffany", "Amber",
        "Samantha", "Destiny", "Candy", "Lexi", "Chanel", "Nikki", "Savannah",
        "Zoe", "Roxie", "Brandi", "Kiki", "Diamond", "Trixie", "Raven",
    ],
    "titles.txt": [
        "Slut", "Sissy", "Bimbo", "Prostitute", "Trans-whore", "Cumdump",
        "Whore", "Cumslut", "Fuckpet", "Cumtoilet", "Hole", "Breeding-whore",
    ],
}

VAGUE = ["a few", "several", "a bunch of", "a handful of", "a pile of",
         "loads of", "dozens of", "a whole row of", "a queue of"]
COUNT_WORDS = ["two", "three", "four", "five", "six", "eight", "ten"]

# ---------------------------------------------------------------- short
SHORT = [
    "I sucked {every} and swallowed every drop.",
    "I sucked {every} and gulped his load.",
    "I gagged hard on {every}.",
    "I got poked by {every} in the throat.",
    "I kissed {every} and {balls}.",
    "I licked {every} and {balls}.",
    "I jerked {every} and {balls} with both hands.",
    "I stroked {every} until it leaked.",
    "I throated {every} until my eyes watered.",
    "I got throated by {cocks} and gaped.",
    "I got fucked by {cocks} in {ass}.",
    "I got dp'd by {cocks} balls deep in {ass}.",
    "{Ass_cap} got stretched out by {cocks}.",
    "I stretched out {ass} on {cock1}.",
    "I let {every} fuck {ass} and cum inside it while I sucked {word}.",
    "I tasted {ass} and sucked {every}.",
    "I licked everyone's asshole before they face fucked me.",
    "I ate everyone's asshole out.",
    "I ate my own cum out of my gaping wide asshole.",
    "I drank {n2} cumshots out of my bukkake bowl and gulped it down like a good whore.",
    "I got used like a good slut.",
    "I got fucked stupid by {cocks}.",
    "I got my ass fucked and my throat used at the same time.",
    "I gaped for {every} and begged to be fucked.",
    "I swallowed {every} load and showed my tongue.",
    "I burped the smell of {smell} {word}.",
    "After I got my nails done I sucked {every}.",
    "I love stretching out my butthole while getting deepthroated in a row by a group of hard big black {word}s.",
    "I love getting smacked by {every} after doing a manicure and pedicure.",
    "I deepthroated {cock1} and swallowed all of his cum while stretching out my asshole.",
    "I worked the corner for money and sucked {every}.",
    "I got paid to take {cocks} in {ass}.",
    "I licked my cum out of his dirty asshole.",
    "I ate his load out of her butthole.",
    "I rimmed {every} before getting fucked.",
    "I played with {every} as soon as I arrived and ripped my clothes off.",
    "I jerked {every} and filled both of my hands and my mouth as soon as I could.",
    "I got smacked by {every} and kept sucking.",
    "I swallowed {every} load and asked for more.",
    "I got fucked by {cocks} and my face was soaked in cum.",
]

# ---------------------------------------------------------------- active
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

# ---------------------------------------------------------------- riding
RIDING = [
    "I {rv} {cock1}{scene} until it wrecked me.",
    "I {rv} {cock1}{scene} and took it balls deep.",
    "I {rv} {cock1}{scene} with my tits swinging.",
    "I {rv} {cock1}{scene} and worked it deeper.",
    "I {rv} {cock1}{scene} until my legs burned.",
    "I {rv} {cock1}{scene} and squirted all over it.",
]

# ---------------------------------------------------------------- special
SPECIAL = [
    "I got dp'd by {cocks} and screamed.",
    "I got gangbanged by {cocks} and gaped.",
    "I got airtight by {cocks} and gulped.",
    "I got spit roasted by {cocks} and took it both ends.",
    "I got triple penetrated by {cocks} and wrecked.",
    "I got hosed down by {cocks} and licked it off my face.",
    "I got passed around by {cocks} until I couldn't count.",
    "I got bred by {cocks} and pushed it back out.",
]

# ---------------------------------------------------------------- rich
RICH = [
    "I gagged like {role} as {cock1} slammed down my throat, {part} while I deepthroated it {end}.",
    "{Poss_ass} dripped {cum} after {cock1} wrecked me in {place}, turning me into {role} for anyone watching.",
    "I rode {cock1} like {role}, {ass} stretched wide as I bounced and begged to be {pet}.",
    "Double penetration destroyed me when {cock1} rammed my pussy and {cock2} tore into {ass}, leaving me {role} leaking mixed loads.",
    "I sucked {toy} then switched to {cock1}, ass-to-mouth like {role}, tasting {ass} on it.",
    "Bukkake covered my face as {cocks} exploded, glazing me until I was {role} swallowing every drop.",
    "I shoved {toy} up {ass} then took {cock1} in my throat, gagging like {role}.",
    "Triple penetration wrecked my holes: {cock1} in ass, {cock2} in pussy, {cock3} down my throat, turning me into {role}.",
    "Cum swapped with another slut after I pulled {cock1} from {ass} and shared the load like {role}.",
    "I deepthroated {cock1} through the gloryhole, gagging violently like {role} until he dumped his load down my gullet.",
    "{Poss_ass} leaked cum after riding {cock1}, the stretch so brutal I crawled like {role}.",
    "I got fucked by {cock1} while a buttplug stretched my other hole, public humiliation like {role} on display.",
]

# ---------------------------------------------------------------- stories
STORY_OPENERS = [
    "{Subj} was at {place} for {reason}, {clothing}, and got on {poss} knees before anyone asked.",
    "{Subj} did it for {reason} and didn't pretend otherwise, mouth already open at {place}.",
    "{Subj} had just had {poss} nails done and went straight to {place} for {reason}, {clothing}.",
    "It started with {number} strangers at {place} and one instruction. {Subj} was there for {reason}.",
    "{Subj} needed {reason} and {place} was where {subj} got it, {clothing}.",
    "The rule at {place} was simple: whatever walked in, {Subj} took. {Subj} was there for {reason}.",
    "{Subj} took the bus to {place} for {reason}, {clothing}, and got on {poss} knees in the doorway.",
    "Somebody at {place} said get comfortable. {Subj} took {poss} clothes off instead, for {reason}.",
    "{Subj} had been warned about {place}. {Subj} went anyway for {reason}, mouth open.",
    "{Subj} was late, {clothing}, and already dripping when {subj} reached {place} for {reason}.",
]

STORY_BEATS = [
    "First came {number} of them, a proper {term}, and {subj} {reaction}.",
    "{Subj} got put {position} and {action} {subject} until {poss} jaw ached.",
    "{Subj} spread {ass} for every {word} in the room and begged.",
    "{Subj} was passed around and {action} {number} of them without a break.",
    "Someone jammed {toy} into {obj} first, then {subj} {action} {subject} like a brainless hole.",
    "{Subj} licked everyone's asshole before they face fucked {obj}.",
    "{Subj} ate every asshole in the room and got {poss} hair pulled for it.",
    "They lined up for a {term} and {subj} {action} {subject} through all of it.",
    "{Subj} {action} {subject} while another {word} reamed {ass}.",
    "{Subj} got {position} and took {subject} balls deep, {reaction}.",
    "A stranger grabbed {poss} hair and {action} {obj} while {subj} {reaction}.",
    "{Subj} gagged hard on everyone's {word} in a row and gulped.",
    "It turned into a {term}: one in {ass}, one in {poss} mouth, one in each hand.",
    "{Subj} got airtight and couldn't breathe around it.",
    "Cum went everywhere, {fluid} across {poss} tits and {poss} chin.",
    "{Subj} got {ass} stretched around {toy} and held there while the room watched.",
    "{Subj} {reaction} as {ass} was reamed until it gaped.",
    "They made {obj} {action} the {word} that had just been in {ass} and {subj} {reaction}.",
    "{Subj} ate {poss} own load out of {poss} gaping wide asshole.",
    "{Subj} licked {poss} cum out of his dirty asshole.",
    "{Subj} got {poss} asshole filled, then {action} it clean, then took another.",
    "Somebody filmed the {term} while {subj} {action} {subject}, {poss} mouth full.",
    "{Subj} got bent over and {action} {subject} while the next one waited.",
    "{Subj} was made to say thank you with a mouthful before {subj} {action} {subject} again.",
    "{Subj} {reaction} while {number} of them finished on {poss} face.",
    "A hand pushed {poss} head down and {subj} {action} {subject} until {subj} saw stars.",
    "{Subj} swapped cum from {ass} straight into {poss} mouth and {reaction}.",
    "{Subj} took {subject} in {ass} and {reaction}, {poss} knees skidding.",
    "{Subj} {action} {subject} while others waited and watched, {poss} ass up.",
    "{Subj} got {ass} plugged and put back to work, {reaction}.",
    "{Subj} was dragged back into position and {action} {subject} without a word.",
    "{Subj} {reaction}, {fluid} everywhere, and still {action} {subject}.",
    "{Subj} got {poss} asshole eaten while {action} {subject}.",
    "{Subj} swallowed {number} loads and opened {poss} mouth to show them.",
    "{Subj} {action} {subject} until {ass} was puffy and gaping.",
]

STORY_NAME_BEATS = [
    "{Name} got {ass} stretched around {toy} and begged for more.",
    "{Name} took {subject} in {ass} and {reaction}.",
    "{Name} was put {position} and used like a toy, {reaction}.",
    "A stranger dragged {Name} back into position by {poss} hair and {action} {subject}.",
    "{Name} got {ass} wrecked by {number} of them while {subj} {reaction}.",
    "{Name} crawled through {fluid} to {action} the next {word}.",
    "{Name} swallowed {number} loads and opened {poss} mouth.",
]

STORY_CLOSERS = [
    "{Subj} finished with {ass} gaping and {fluid} down both thighs, still {clothing}.",
    "When it was over {subj} lay in a puddle of {fluid}, {poss} asshole twitching.",
    "They left {obj} there, {clothing}, leaking {fluid}, grinning stupidly.",
    "{Subj} crawled home with {ass} wrecked and {fluid} soaking through {poss} clothes.",
    "The last thing {subj} did was {action} the final {word} clean and swallow.",
    "{Subj} got used like a good slut at the end and where it counts.",
    "{Subj} ate {poss} own cum out of {poss} gaping wide asshole and thanked them.",
    "Somebody took a photo of {obj} sprawled in {fluid}, {poss} asshole ruined.",
    "{Subj} got dressed in {clothing} that was already soaked and limped out.",
    "{Subj} wiped {fluid} off {poss} chin and limped home with the money.",
    "They counted {number} loads between them and {subj} swallowed the last one.",
    "{Subj} left {place} used up, gaping, {fluid} everywhere, already planning the next visit.",
]

CATEGORIES = {
    "bbc": {"label": "big black", "tag": "bbc"},
    "bwc": {"label": "big white", "tag": "bwc"},
    "any": {"label": "any colour", "tag": "any"},
    "group": {"label": "gangbang / dp / spit roast", "tag": None,
              "passive": ("gang", "dp'd", "tp'd", "spit roasted", "passed", "drilled", "airtight")},
    "oral": {"label": "sucking / gagging", "tag": None,
             "passive": ("throat", "mouth", "face")},
    "atm": {"label": "ass to mouth / creampie", "tag": None,
            "passive": ("creampied", "bred", "pumped full", "hosed")},
    "public": {"label": "public", "tag": None, "scene_heavy": True},
    "prostitution": {"label": "prostitution", "tag": None},
    "toys": {"label": "toys", "tag": None, "toy_heavy": True},
}

STORY_THEMES = {
    "gloryhole": {"label": "Gloryhole marathon", "place": ("gloryhole", "bathroom", "rest-stop")},
    "party": {"label": "House party train", "place": ("party", "balcony", "mattress")},
    "reststop": {"label": "Truck stop relay", "place": ("rest-stop", "truck", "shower")},
    "upside": {"label": "Upside down", "position": ("upside",)},
    "sissy": {"label": "Sissy initiation", "clothing": ("collar", "socks", "lace")},
    "bimbo": {"label": "Bimbo audition", "modifier": ("bimbo", "tits")},
    "street": {"label": "Prostitute shift", "place": ("alley", "doorway", "counter", "corner")},
    "motel": {"label": "Motel toy warmup", "place": ("motel", "mattress"),
              "toy": ("plug", "dildo", "machine")},
    "sauna": {"label": "Sauna", "place": ("sauna", "shower")},
    "salon": {"label": "Salon back room", "place": ("salon",),
              "clothing": ("nails", "heels", "fishnet")},
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
    for _ in range(6):
        new = TOKEN.sub(lambda m: slots.get(m.group(1), m.group(0)), template)
        if new == template:
            break
        template = new
    return template


def _article(word: str) -> str:
    return "an" if word[:1].lower() in "aeiou" else "a"


def _adjs(tag=None) -> list:
    rows = []
    for line in load("kinds.txt"):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 2:
            rows.append(parts[:2])
    if tag and tag != "any":
        hits = [r for r in rows if tag in r[1].split(",")]
        if hits:
            return [r[0] for r in hits]
    return [r[0] for r in rows] or ["big black"]


def _cocks(tag=None, style=None, word=None) -> str:
    """One noun per sentence: caller passes the word so it never mixes."""
    word = word or random.choice(["cock", "dick"])
    adj = random.choice(_adjs(tag))
    plural = word + "s"
    if style is None:
        r = random.random()
        if r < 0.20:
            style = "single"
        elif r < 0.34:
            style = "digit"
        elif r < 0.46:
            style = "word"
        elif r < 0.70:
            style = "everyone"
        elif r < 0.86:
            style = "vague"
        else:
            style = "bare"
    if style == "single":
        return f"{_article(adj)} {adj} {word}"
    if style == "digit":
        return f"{random.randint(2, 9)} {adj} {plural}"
    if style == "word":
        return f"{random.choice(COUNT_WORDS)} {adj} {plural}"
    if style == "everyone":
        return f"everyone's {adj} {word}"
    if style == "vague":
        return f"{random.choice(VAGUE)} {adj} {plural}"
    return f"{adj} {plural}"


def _scene(chance: float) -> str:
    return " " + random.choice(load("scenes.txt")) if random.random() < chance else ""


def _n2() -> str:
    return random.choice(["two", "two", "three", "3", "4", "a few"])


def _role() -> str:
    r = random.choice(load("roles.txt"))
    return f"{_article(r)} {r}"


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
    word = random.choice(["cock", "dick"])          # locked for the sentence
    scene_chance = 0.40 if spec.get("scene_heavy") else 0.18
    if intensity == 1:
        scene_chance *= 0.4
    if intensity == 3:
        scene_chance = min(0.7, scene_chance + 0.2)

    rich_share = {1: 0.10, 2: 0.25, 3: 0.50}.get(intensity, 0.25)
    roll = random.random()

    slots = {"poss": "my", "obj": "me", "subj": "I", "be": "am", "word": word,
             "cock1": _cocks(tag, "single", word),
             "cock2": _cocks(tag, "single", word),
             "cock3": _cocks(tag, "single", word)}

    if roll < rich_share:
        tpl = random.choice(RICH)
        slots.update(
            gv=random.choice(load("gag_verbs.txt")),
            tv=random.choice(load("throat_verbs.txt")),
            part=random.choice(load("participles.txt")),
            end=random.choice(load("ends.txt")),
            pet=random.choice(load("pets.txt")),
            role=_role(),
            place=random.choice(load("places.txt")),
            toy=random.choice(load("toys.txt")),
            cum=random.choice(load("cum.txt")),
            cocks=_cocks(tag, None, word),
            ass=random.choice(load("dirty_ass.txt")),
        )
        slots["Poss_ass"] = _cap(slots["ass"])
        text = fill(tpl, slots)
    else:
        sub = random.random()
        if sub < 0.18:
            tpl = random.choice(SPECIAL)
        elif sub < 0.34:
            tpl = random.choice(RIDING)
        elif sub < 0.56:
            tpl = random.choice(ACTIVE)
        else:
            tpl = random.choice(SHORT)

        if "{rv}" in tpl:
            slots.update(rv=random.choice(load("riding_verbs.txt")),
                         cock1=_cocks(tag, "single", word),
                         scene=_scene(scene_chance))
        elif "{pv}" in tpl:
            slots.update(pv=random.choice(_narrow(load("passive_verbs.txt"), spec.get("passive"))),
                         cocks=_cocks(tag, None, word), scene=_scene(scene_chance),
                         hole=random.choice(load("holes.txt")))
        elif "{av}" in tpl:
            slots.update(av=random.choice(load("active_verbs.txt")),
                         cocks=_cocks(tag, None, word),
                         tail=random.choice(load("oral_tails.txt")),
                         scene=_scene(scene_chance))
        else:
            slots.update(cocks=_cocks(tag, None, word), n2=_n2(),
                         cum=random.choice(load("cum.txt")))

        slots.setdefault("every", _cocks(tag, "everyone", word))
        slots.setdefault("balls", random.choice(load("balls.txt")))
        slots.setdefault("ass", random.choice(load("dirty_ass.txt")))
        slots.setdefault("smell", random.choice(load("smells.txt")))
        slots["Ass_cap"] = _cap(slots["ass"])
        slots.setdefault("place", random.choice(load("places.txt")))

        text = fill(tpl, slots)
        second = {1: 0.0, 2: 0.25, 3: 0.45}.get(intensity, 0.25)
        if "." not in text[:-1] and random.random() < second:
            text = text.rstrip(".") + ". " + random.choice(load("faces.txt"))
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
    word = random.choice(["cock", "dick"])
    slots = {
        "Subj": "I" if first else name,
        "subj": "I" if first else "she",
        "poss": "my" if first else "her",
        "obj": "me" if first else "her",
        "be": "am" if first else "is",
        "Name": name,
        "word": word,
        "role": _role(),
        "subject": _cocks(spec.get("tag"), random.choice(
            ["single", "single", "everyone", "digit", "vague"]), word),
        "ass": random.choice(load("dirty_ass.txt")),
        "balls": random.choice(load("balls.txt")),
        "term": random.choice(load("gangbang_terms.txt")),
        "reason": random.choice(load("reasons.txt")),
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
                 "sound", "toy", "number", "modifier", "action", "ass"):
        slots[slot] = fill(slots[slot], slots)
    return slots


def _story_actions() -> list:
    return [v[:-3] if v.endswith(" by") else v for v in load("passive_verbs.txt")] + \
           load("active_verbs.txt")


def generate_story(beats: int = 8, theme: str = "random", pov: str = "third",
                   intensity: int = 2) -> str:
    names, titles = load("names.txt"), load("titles.txt")
    name = random.choice(names) if names else "Ashley"
    use_title = random.random() < 0.5
    title = random.choice(titles) if (use_title and titles) else ""
    spec = dict(STORY_THEMES.get(theme, {}))

    parts = [fill(random.choice(STORY_OPENERS), _story_slots(spec, name, pov))]

    name_uses = 1
    last_was_name = True
    for _ in range(max(1, beats)):
        s = _story_slots(spec, name, pov)
        want_name = (pov == "third" and not last_was_name and name_uses < 2
                     and random.random() < 0.22)
        if want_name:
            parts.append(fill(random.choice(STORY_NAME_BEATS), s))
            name_uses += 1
            last_was_name = True
        else:
            parts.append(fill(random.choice(STORY_BEATS), s))
            last_was_name = False
        if intensity >= 3 and random.random() < 0.3:
            parts.append(fill(random.choice(load("reactions.txt")), s) + ".")

    parts.append(fill(random.choice(STORY_CLOSERS), _story_slots(spec, name, pov)))
    body = "\n\n".join(polish(p) for p in parts if p.strip())
    heading = _cap(theme if theme != "random" else "dirty story")
    who = f"{title} {name}" if title else name
    return f"=== {heading}: {who} ===\n\n{body}\n"


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
        print(f"  {name:<20} {n:>4}{'   <-- thin' if n < 5 else ''}")
    required = ("kinds.txt", "passive_verbs.txt", "active_verbs.txt", "roles.txt",
                "balls.txt", "dirty_ass.txt", "rim.txt", "eat_cum.txt")
    print("\nRequired pools:", "OK" if all(len(load(f)) >= 4 for f in required) else "THIN")


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
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modular Explicit Phrase & Story Engine (v5.0)
=============================================
Uncensored modular generator. All vocabulary lives in editable .txt files under
data/ -- the engine only holds grammar, categories and story structure.

v5.0 over v4.0:
  * 5x larger pools + 8 new pools (holes, positions, places, fluids, reactions,
    clothing, sounds, toys, numbers, modifiers)
  * template-driven sentences with a fixed grammatical contract per slot,
    replacing the substring-branch spaghetti
  * dynamic counts everywhere -- no more hardcoded "8 guys" / "6 dicks"
  * story mode rebuilt as opener -> beats -> closer, with themes and POV switch
  * intensity levels, dedupe, seeding, category filters, CLI, txt/md/html/json
  * settings gained default_beats / default_intensity, with validation
"""

from __future__ import annotations

import argparse
import html
import json
import random
import re
import sys
from pathlib import Path

VERSION = "5.0"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SETTINGS_FILE = BASE_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "default_count": 50,
    "default_beats": 8,
    "default_intensity": 2,
    "default_phrase_filename": "explicit_phrases.txt",
    "default_story_filename": "dirty_story.txt",
}

# ---------------------------------------------------------------------------
# Slot contracts
#   action    -> past-tense verb phrase, may contain {poss}
#   subject   -> cock noun phrase, article baked in
#   place     -> noun phrase usable after "at/in/on" or bare
#   context   -> trailing clause, starts lowercase, ends with "."
#   role      -> bare noun phrase (article added at pick time)
#   hole      -> "my asshole" style, {poss} substituted
#   position  -> body-position phrase
#   fluid     -> cum/lube noun phrase
#   reaction  -> verb phrase, may contain {poss}
#   clothing  -> what is (barely) worn
#   sound     -> noun phrase for "over the sound of ..."
#   toy       -> toy noun phrase, article baked in
#   number    -> spelled-out count
#   modifier  -> comma-separated modifier phrase
#   actor     -> "I" or the persona name
#   poss      -> "my" or "her"
# ---------------------------------------------------------------------------

DEFAULT_DATA = {
    "actions.txt": [
        "choked on", "gagged on", "slobbered all over", "deepthroated",
        "face-fucked myself on", "swallowed to the balls", "sucked like a starving whore",
        "buried {poss} nose in the balls of", "took past the gag reflex",
        "licked clean", "slurped on", "hummed around", "rode cowgirl on",
        "rode reverse cowgirl on", "backed onto", "took balls-deep in one shove",
        "got split open by", "got pounded by", "took doggy-style",
        "got railed against the wall by", "was folded in half by",
        "was used like a fleshlight by", "took in double penetration",
        "was triple penetrated by", "got spit-roasted by", "got airtight-stuffed by",
        "got fisted by", "got gaped wide by", "took in every hole at once",
        "was passed between", "was handed around to", "drained", "milked dry",
        "got face-fucked by", "was put upside down and face-fucked by",
        "got throat-fucked by", "got {poss} ass eaten by", "ate out", "rimmed",
        "got creampied by", "got bred by", "got loaded by", "took the load from",
        "got cum dumped into", "swapped cum with", "snowballed with",
        "licked {poss} own creampie out of", "got slapped by", "got spanked raw by",
        "got held down and reamed by", "got drilled from behind by", "got wrecked by",
        "bounced on", "got stretched around", "spread {poss} cheeks wide for",
        "pushed back onto", "begged for", "got plugged by", "got machine-fucked by",
        "took the whole fist from", "got double-stuffed by", "got hosed down by",
        "gulped down", "worked {poss} tongue around", "slapped {poss} own face with",
        "stuffed {poss} throat with", "let {poss} jaw go slack for",
    ],
    "subjects.txt": [
        "that massive big black cock", "that throbbing BBC", "that heavy black shaft",
        "an enormous black dick", "a fat veiny BWC", "that monster cock",
        "that massive big white cock", "that thick BWC", "a pale uncut white cock",
        "two mixed cocks", "a train of strangers' cocks", "anonymous gloryhole cocks",
        "a black cock thicker than {poss} wrist", "a hard young white cock",
        "three cocks in rotation", "a pair of hard mixed cocks",
        "the biggest BBC {actor} could take", "a slick ebony shaft",
        "a long pink white-boy cock", "a fat-headed BWC", "a sweaty stranger's cock",
        "a black cock with a vein running down the shaft", "two black and one white",
        "a line of cocks waiting behind {obj}", "a cock that split {obj} open",
        "that heavy-hanging black dick", "a soft-then-iron-hard white cock",
        "a monster black dick and a thick white one together",
    ],
    "places.txt": [
        "the truck-stop gloryhole", "the rest-stop bathroom", "the club bathroom stall",
        "the alley behind the bar", "the park bench", "the stairwell",
        "the laundromat", "the motel room", "the gym sauna", "the truck cab",
        "the balcony", "the back room", "the parking garage", "the picnic table",
        "the changing room", "the doorway after closing", "the bare mattress on the floor",
        "the house party", "the bushes at the park edge", "under the bridge",
        "the shower block", "the counter of a closed shop", "the taxi back seat",
        "the cheap hotel corridor", "the football club locker room",
    ],
    "contexts.txt": [
        "until tears streamed down {poss} face.",
        "while getting drilled from behind at the truck-stop gloryhole.",
        "like a desperate slut at the rest-stop bathroom.",
        "until {poss} jaw locked completely.",
        "while {poss} gaping asshole got wrecked.",
        "until {poss} loose hole leaked thick ropes.",
        "while strangers filmed every second.",
        "until warm cum filled {poss} throat and bubbled out {poss} nose.",
        "while crying on the dirty bathroom floor.",
        "until thick cum poured out of {poss} gaping asshole.",
        "leaving a puddle of jizz on the tiles.",
        "with cumshots all over {poss} face.",
        "until {actor} saw stars and {poss} legs gave out.",
        "while the whole room watched.",
        "like a brainless fucktoy.",
        "until {actor} couldn't remember {poss} own name.",
        "with spit ropes swinging off {poss} chin.",
        "until {poss} voice went hoarse from gagging.",
        "leaving {obj} a twitching, leaking mess.",
        "so everyone saw exactly what a cheap cumdump {actor} {be}.",
        "until {actor} thanked them with a mouthful.",
        "with creampie running down both thighs.",
        "until {poss} hole was puffy and winking.",
        "and swallowed every drop like a good little hole.",
        "with {poss} makeup smeared into {poss} eyes.",
        "until {poss} thighs were slick to the knee.",
        "while {poss} caged clitty leaked pathetically.",
        "leaving {poss} hole open and winking at the ceiling.",
        "until the only word left in {poss} head was more.",
        "with {poss} tits bouncing and slick with spit.",
    ],
    "roles.txt": [
        "worthless sissy whore", "brainless bimbo cumslut", "pathetic cumslave",
        "cheap street prostitute", "gaping anal slut", "desperate gloryhole cumdump",
        "humiliated public whore", "stretched asshole slave", "gagging deepthroat slut",
        "bukkake cumtoilet", "trans-whore slut", "drooling anal addict",
        "brain-dead cock sleeve", "rented gloryhole hole", "truck-stop cumdump",
        "bimbo breeding whore", "sissy anal cockslut", "public-use cumdump",
        "ATM-obsessed filth slut", "double-stuffed ass whore", "wrecked little sissy pet",
        "cum-swapping cumslut", "plugged bimbo hole", "cock-drunk street whore",
        "slobbering throat slave", "loose-holed anal whore", "eager little cum sponge",
        "braindead bukkake toy", "milking-machine cumslut", "back-alley anal whore",
        "swollen-holed fuckpet", "clitty-caged sissy pet", "fake-tit bimbo fucktoy",
        "ass-to-mouth filth whore", "triple-penetration cumrag", "used-up cuntboy",
        "hotel-corridor whore", "locker-room cumdump", "sauna steam-room slut",
        "six-man spit-roast toy", "gloryhole regular", "cum-guzzling bimbo",
    ],
    "holes.txt": [
        "{poss} ass", "{poss} asshole", "{poss} butthole", "{poss} gaping asshole",
        "{poss} sloppy hole", "{poss} throat", "{poss} mouth", "{poss} cunt",
        "{poss} loose ass", "{poss} wrecked hole", "{poss} plug-stretched hole",
        "{poss} open ass", "{poss} stretched-out butthole", "{poss} ruined little hole",
    ],
    "positions.txt": [
        "doggy with {poss} face pushed into the dirt", "on {poss} back, legs over his shoulders",
        "reverse cowgirl with {poss} ass jiggling", "cowgirl with {poss} hands on his chest",
        "flat on {poss} belly", "folded in half", "standing against the wall",
        "on {poss} knees with {poss} hands behind {poss} back", "upside down",
        "spread-eagle", "spooned from behind", "in a deep squat",
        "bent over the bench with {poss} heels lifted", "tied to the rail",
        "holding {poss} own ankles", "in a headlock on the cock",
        "bent over the sink", "braced on the tiles", "straddling him backwards",
        "pressed to the wall with {poss} cheek flat",
    ],
    "fluids.txt": [
        "thick ropes of cum", "warm loads", "a fat creampie", "sloppy seconds",
        "a mouthful of cum", "drips of precum", "lube and spit",
        "a puddle of mixed loads", "stringy cum", "a hot sticky mess",
        "a fresh hot load", "overflowing cum", "spit and lube",
        "a slow leaking creampie", "a face full of cum", "runny seconds",
    ],
    "reactions.txt": [
        "rolled {poss} eyes back", "curled {poss} toes", "let {poss} legs shake",
        "whined around it", "arched {poss} back", "leaked down {poss} thigh",
        "babbled nonsense", "drooled on {poss} own tits", "went cross-eyed",
        "shuddered and clenched", "gasped for air", "groaned like an animal",
        "begged out loud", "hiccuped around the shaft", "melted into the floor",
        "shook all over", "moaned with {poss} mouth full", "grinned stupidly",
    ],
    "clothing.txt": [
        "nothing but a collar", "knee-high socks and heels", "a short skirt hiked to the waist",
        "torn fishnets", "a crop top pulled down under {poss} tits",
        "heels and nothing else", "a lace bodysuit pulled to the side",
        "a plug with a jewel base", "a leash clipped to {poss} collar",
        "a tiny thong pushed aside", "a school skirt with no underwear",
        "a mesh top and nothing under it", "a PVC harness", "tights torn at the crotch",
        "a soaked g-string", "a hoodie and socks, nothing else",
    ],
    "sounds.txt": [
        "wet slaps", "a loud squelch", "gagging and slurping", "a low groan",
        "slurping and gulping", "the clack of the plug", "ragged breathing",
        "skin on skin", "sloppy wet sucking", "the squeak of a rubber sole",
        "dripping on the tiles", "a wet pop as it pulled out",
        "the hum of the machine", "a muffled whimper",
    ],
    "toys.txt": [
        "a massive knotted dildo", "an inflatable buttplug pumped to the max",
        "a ribbed horse-cock dildo", "a thrusting fuck-machine dildo",
        "a stack of glass and silicone dildos", "a fist-sized plug",
        "a vibrating wand taped to a plug", "a tapered trainer set, all at once",
        "a huge suction-cup dildo", "a beaded steel plug pulled out ball by ball",
        "a thick double-ended dildo", "a hollow plug that leaks lube",
        "a weighted egg plug", "a spinning, rotating anal toy",
        "a soft-then-hard inflatable plug", "a heavy steel plug with a jewel base",
        "a knotted tentacle dildo", "a glass plug warmed under the tap",
        "a fat silicone dildo with a knot at the base", "a speculum",
    ],
    "numbers.txt": [
        "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "a dozen", "fifteen", "twenty",
    ],
    "modifiers.txt": [
        "in full sissy lingerie with {poss} makeup running",
        "with a buttplug keeping {poss} other hole stretched open",
        "after wrecking {obj} stupid with toys first",
        "with {poss} fake bimbo tits bouncing and slick with spit",
        "publicly, so anyone passing could watch the humiliation",
        "with {poss} caged clitty leaking down {poss} thigh",
        "with {poss} makeup ruined and {poss} hair a mess",
        "with spit ropes hanging off {poss} chin",
        "still wearing {poss} plug and dripping lube",
        "with a crowd of strangers watching and filming",
        "barely able to keep {poss} eyes open",
        "with {poss} ass already red from spanking",
        "after being passed around for an hour",
        "with {poss} throat already raw from gagging",
        "in nothing but knee-high socks and a collar",
        "with {poss} hands tied behind {poss} back",
        "smelling of lube, cum and cheap perfume",
        "with {poss} tights torn open at the crotch",
        "with {poss} bra pulled down under {poss} tits",
        "with a plug still humming on low inside {obj}",
        "in ruined drag makeup",
        "with {poss} knees skinned from the concrete",
        "with {poss} hole still dripping from the last one",
        "with a leash in a stranger's fist",
    ],
    "names.txt": [
        "Ashley", "Trina", "Chloe", "Brittany", "Jessica", "Tiffany", "Amber",
        "Samantha", "Destiny", "Candy", "Lexi", "Chanel", "Nikki", "Savannah",
        "Zoe", "Roxie", "Brandi", "Kiki", "Diamond", "Trixie", "Misty", "Raven",
    ],
    "titles.txt": [
        "Mistress", "Slut", "Sissy", "Bimbo", "Prostitute", "Trans-whore",
        "Cumdump", "Whore", "Slut-puppet", "Cumslut", "Fuckpet", "Cumtoilet",
        "Hole", "Cock-sleeve", "Breeding-whore",
    ],
}

# ---------------------------------------------------------------------------
# Sentence templates. Every slot has a fixed position contract.
# ---------------------------------------------------------------------------
TEMPLATES = [
    "I {action} {subject} at {place} as {role} {modifier}, {context}",
    "As {role} I {action} {subject} at {place} {modifier}, {context}",
    "I shoved {toy} into {hole}, then {action} {subject} at {place} like {role}, {context}",
    "{Poss} throat and {hole} got destroyed when I {action} and then {action} {subject} at {place} as {role}, {context}",
    "I was {role} getting {action} by {subject} while I {action} another, {modifier}, {context}",
    "There I was, {role} at {place} {modifier}, and I {action} {subject}, {context}",
    "At {place}, {role} like me {action} {subject} {modifier}, {context}",
    "{Position_cap}, I {action} {subject}, {modifier}, {context}",
    "I {action} {subject} at {place} {modifier} as {role}, {context}",
    "At {place} I {action} {subject} {modifier} and got {hole} wrecked like {role}, {context}",
    "Nobody asked -- I just {action} {subject} at {place} {modifier} like {role}, {context}",
    "I got into position: {position}, and {action} {subject} {modifier}, {context}",
    "Plugged with {toy}, {modifier}, I {action} {subject} at {place} like {role}, {context}",
    "It started with {toy} and ended with {subject} at {place}, and I took it like {role}, {context}",
    "Every hole filled, I {action} {subject} at {place} {modifier}, {context}",
    "I {action} {subject} {modifier} at {place} and {action} it like {role}, {context}",
    "{Number_cap} of them took turns at {place}: one made me {action} {subject} while another wrecked {hole}, {modifier}, {context}",
    "Down on {poss} knees at {place}, I {action} {subject}, {modifier}, {context}",
    "I {action} {subject} while a second cock pushed at {poss} lips at {place}, {modifier}, {context}",
    "Somebody's fist in {poss} hair, I {action} {subject} at {place} {modifier} as {role}, {context}",
    "{Sound_cap} behind me, I {action} {subject} at {place} as {role} {modifier}, {context}",
    "I {action} {subject} until {fluid} ran down {poss} chin at {place}, {modifier}, {context}",
    "Wearing {clothing}, I {action} {subject} at {place} like {role} {modifier}, {context}",
    "{Role_cap} on all fours at {place}, taking {subject}, {modifier}, {context}",
    "I {action} {subject} at {place} and {reaction}, {modifier}, {context}",
]

# ---------------------------------------------------------------------------
# Story structure
# ---------------------------------------------------------------------------
STORY_OPENERS = [
    "{actor} knelt on the tile of {place}, wearing {clothing}, mouth already open and waiting.",
    "It began with {number} strangers and one instruction: get on {poss} knees at {place}.",
    "{actor} had no plan for the night beyond {place}, {clothing}, and a hole that needed filling.",
    "The door to {place} hadn't even shut before {actor} was down on {poss} knees, {clothing}.",
    "{actor} was late, {clothing}, and already dripping when {actor} reached {place}.",
    "Somebody at {place} said get comfortable. {actor} got {poss} clothes off instead.",
    "{actor} came to {place} for one thing and got {number} of them, {clothing}.",
    "By the time the light came on in {place}, {actor} was {clothing} and shaking.",
    "The rule at {place} was simple: whatever walked in, {actor} took, {clothing}.",
    "{actor} had been warned about {place}. {actor} went anyway, {clothing}, mouth open.",
    "It started as a joke at {place} and ended with {actor} face down in {fluid}, {clothing}.",
    "{actor} stood in the middle of {place}, {clothing}, and let the room decide.",
]

STORY_BEATS = [
    "First came {number} strangers who took turns {action} {subject} while {actor} {reaction}.",
    "{actor} got put {position} and {action} {subject} until {poss} jaw ached.",
    "{actor} loved spreading {poss} {hole} for every big black cock and big white cock that walked in.",
    "{actor} was handed around the room and {action} {number} of them without a break.",
    "Someone pushed {toy} into {obj} first, then {actor} {action} {subject} like a brainless hole.",
    "Over the sound of {sound}, {actor} {reaction} and {action} {subject} until {poss} throat bulged.",
    "{actor} got {position} and took {subject} balls-deep, {reaction}.",
    "A stranger grabbed {poss} hair and {action} {obj} while {actor} {reaction}.",
    "{actor} begged for it, so they gave {obj} {number} at once, {reaction}.",
    "They swapped out and {actor} {action} {subject} again, {poss} face a mess of {fluid}.",
    "{actor} {action} {subject} while another cock wrecked {poss} {hole} at the same time.",
    "At one point {actor} got face-fucked upside down and {poss} jaw went slack, {fluid} running everywhere.",
    "{actor} was told to hold {poss} cheeks open, and {number} of them used the invitation.",
    "{actor} {action} {subject} until {poss} eyes watered and {poss} mascara ran.",
    "{actor} got {position} and {number} cocks took turns in {poss} {hole}.",
    "They made {obj} {action} the cock that had just been in {poss} ass, and {actor} {reaction}.",
    "{actor} {action} {subject} while {number} pairs of hands held {obj} still.",
    "Cum went everywhere: {fluid} across {poss} tits, {poss} chin, {poss} hair.",
    "{actor} got {poss} {hole} stretched around {toy} and held there while the room watched.",
    "{actor} {reaction} as {poss} {hole} was reamed until it gaped and winked.",
    "{actor} was folded up and {action} {subject} like a toy, {reaction}.",
    "Somebody filmed it all while {actor} {action} {subject}, {poss} mouth full and {reaction}.",
    "{actor} got bent over and {action} {subject} while the next one waited {poss} turn.",
    "{actor} {action} {subject}, then {action} the next, then the next, {poss} chin soaked.",
    "They stopped counting after {number}, and {actor} just kept {action} whatever was put in front of {obj}.",
    "{actor} {reaction} and {action} {subject} with {fluid} dripping off {poss} chin.",
    "{actor} was made to say thank you with a mouthful before {actor} {action} {subject} again.",
    "{actor} got {poss} {hole} filled, then {action} it clean, then took another.",
    "{actor} {reaction} while {number} of them finished on {poss} face and tits.",
    "{actor} got {position} again and {action} {subject} until {poss} voice gave out.",
    "{actor} {action} {subject} sloppy and loud, {sound} filling the room.",
    "A hand pushed {poss} head down and {actor} {action} {subject} until {actor} saw stars.",
    "{actor} swapped cum from {poss} ass straight into {poss} mouth and {reaction}.",
    "{actor} took {subject} in {poss} {hole} and {reaction}, {poss} knees skidding.",
    "{actor} {action} {subject} while {number} others waited and watched, {poss} ass up.",
    "{actor} got {poss} {hole} plugged and put back to work, {reaction}.",
    "{actor} was dragged back into position and {action} {subject} without a word.",
    "{actor} {reaction}, {fluid} everywhere, and still {action} {subject}.",
]

STORY_CLOSERS = [
    "{actor} finished with {poss} hole gaping and {fluid} running down both thighs, still {clothing}.",
    "When it was over {actor} lay in a puddle of {fluid}, {poss} {hole} twitching and open.",
    "They left {obj} there, {clothing}, leaking {fluid}, with a smile that wouldn't come off.",
    "{actor} crawled home with {poss} {hole} wrecked, {fluid} soaking through {poss} clothes.",
    "The last thing {actor} did was {action} the final cock clean and swallow, {fluid} dripping.",
    "{actor} stayed on the floor long after they left, {poss} {hole} winking at the ceiling.",
    "Somebody took a photo of {obj} sprawled out in {fluid}, {poss} hole ruined, and {actor} grinned.",
    "{actor} got dressed in {clothing} that was already soaked and limped out, {poss} hole still open.",
    "By morning {poss} {hole} was puffy and sore and {actor} wanted it all over again.",
    "{actor} wiped {fluid} off {poss} chin with the back of {poss} hand and thanked every one of them.",
    "They counted {number} loads between them and {actor} swallowed the last one on {poss} knees.",
    "{actor} left {place} used up, gaping, {fluid} everywhere, and already planning the next visit.",
]

# ---------------------------------------------------------------------------
# Category filters: slot -> substrings. Unmatched filters fall back to full pool.
# ---------------------------------------------------------------------------
CATEGORIES = {
    "bbc_anal": {
        "label": "BBC + anal + gaping",
        "subject": ("black", "bbc", "ebony"),
        "action": ("ass", "anal", "split", "gaped", "reamed", "drilled", "fisted", "double", "triple"),
        "hole": ("ass", "hole", "butthole"),
        "role": ("anal", "gape", "stretched", "hole"),
    },
    "bwc_oral": {
        "label": "BWC + sucking + gagging",
        "subject": ("white", "bwc"),
        "action": ("choked", "gagged", "throat", "suck", "swallow", "deepthroat", "jaw"),
        "role": ("throat", "gagging", "cockslut"),
    },
    "group": {
        "label": "Group + DP/TP + bukkake",
        "subject": ("two", "three", "train", "line", "pair", "both", "mixed"),
        "action": ("double", "triple", "passed", "handed", "spit-roast", "airtight"),
        "role": ("triple", "cumdump", "spit-roast", "bukkake", "cumrag"),
    },
    "sissy_bimbo": {
        "label": "Sissy + bimbo + cumslut",
        "role": ("sissy", "bimbo", "cumslut", "cumslave", "fuckpet", "cuntboy"),
        "modifier": ("sissy", "bimbo", "clitty", "collar", "lingerie", "leash"),
        "clothing": ("collar", "heels", "fishnet", "plug", "lace"),
    },
    "public_whore": {
        "label": "Public + gloryhole + prostitute",
        "place": ("gloryhole", "rest-stop", "bathroom", "alley", "park", "doorway", "stairwell", "laundromat", "bridge"),
        "role": ("prostitute", "whore", "public", "gloryhole", "rented", "street"),
        "modifier": ("publicly", "crowd", "passing"),
    },
    "toys_trans": {
        "label": "Toys + transgender",
        "toy": ("plug", "dildo", "machine", "inflatable", "wand", "bead", "egg", "tentacle", "speculum"),
        "modifier": ("toy", "plug", "lube", "clitty"),
        "role": ("trans", "sissy", "plugged"),
    },
    "atm_creampie": {
        "label": "ATM + creampie + breeding",
        "action": ("swapped", "snowballed", "licked", "creampied", "bred", "loaded"),
        "fluid": ("creampie", "load", "seconds", "cum"),
        "role": ("ass-to-mouth", "creampie", "breeding", "cum-swapping", "cum-guzzling"),
    },
    "cumdump_bukkake": {
        "label": "Cumdump + bukkake + cumtoilet",
        "role": ("cumdump", "cumtoilet", "cumslave", "cumrag", "sponge"),
        "fluid": ("cum", "load", "mess", "ropes"),
        "modifier": ("crowd", "filming", "publicly"),
    },
    "marathon": {
        "label": "Marathon + numbers + relay",
        "number": ("dozen", "ten", "eleven", "twelve", "fifteen", "twenty"),
        "action": ("passed", "handed", "drained", "milked", "took turns"),
        "context": ("until", "leaving", "so everyone"),
    },
}

STORY_THEMES = {
    "gloryhole": {"label": "Gloryhole marathon", "place": ("gloryhole", "bathroom", "rest-stop")},
    "party": {"label": "House party train", "place": ("party", "balcony", "mattress")},
    "reststop": {"label": "Truck-stop relay", "place": ("rest-stop", "truck", "shower")},
    "upside": {"label": "Upside-down torture", "role": ("throat", "gagging"), "position": ("upside",)},
    "sissy": {"label": "Sissy initiation", "role": ("sissy", "cuntboy", "pet"), "clothing": ("collar", "socks", "lace")},
    "bimbo": {"label": "Bimbo audition", "role": ("bimbo", "cumslut", "toy"), "modifier": ("bimbo", "tits")},
    "street": {"label": "Prostitute shift", "place": ("alley", "doorway", "counter"), "role": ("prostitute", "street", "whore")},
    "motel": {"label": "Motel toy warmup", "place": ("motel", "mattress", "hotel"), "toy": ("plug", "dildo", "machine")},
    "sauna": {"label": "Sauna steam room", "place": ("sauna", "shower", "locker"), "role": ("steam-room", "cumdump")},
    "gangbang": {"label": "Full gangbang", "number": ("eight", "ten", "dozen", "fifteen")},
    "cumswap": {"label": "Cumswap session", "action": ("swapped", "snowballed", "licked"), "fluid": ("cum", "seconds")},
    "laundromat": {"label": "Laundromat quickie", "place": ("laundromat", "stairwell", "taxi")},
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Explicit Engine __VERSION__</title>
<style>
  body { background:#111; color:#eee; font:16px/1.65 Georgia, serif; margin:0; padding:2rem; }
  h1 { font-size:1.15rem; letter-spacing:.14em; text-transform:uppercase; color:#e8557f; }
  h2 { font-size:.95rem; letter-spacing:.1em; text-transform:uppercase; color:#9aa; margin-top:2rem; }
  ol, p { max-width:62rem; }
  li { margin-bottom:.85rem; padding-bottom:.85rem; border-bottom:1px solid #262626; }
  .story p { text-indent:1.4em; }
</style>
</head>
<body>
<h1>Explicit Engine __VERSION__ &mdash; __COUNT__ __NOUN__</h1>
__BODY__
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def bootstrap_data() -> None:
    ensure_directories()
    for filename, lines in DEFAULT_DATA.items():
        path = DATA_DIR / filename
        if not path.exists():
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_txt_file(filename: str) -> list:
    ensure_directories()
    path = DATA_DIR / filename
    if not path.exists():
        if filename in DEFAULT_DATA:
            path.write_text("\n".join(DEFAULT_DATA[filename]) + "\n", encoding="utf-8")
        else:
            return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def load_settings() -> dict:
    if SETTINGS_FILE.exists():
        try:
            merged = DEFAULT_SETTINGS.copy()
            merged.update(json.loads(SETTINGS_FILE.read_text(encoding="utf-8")))
            return merged
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")


def _article(noun: str) -> str:
    return "an" if noun[:1].lower() in "aeiou" else "a"


def _pick(pool, keys=None) -> str:
    if not pool:
        return ""
    if keys:
        narrowed = [item for item in pool if any(k in item.lower() for k in keys)]
        if narrowed:
            return random.choice(narrowed)
    return random.choice(pool)


def _cap(text: str) -> str:
    return text[0].upper() + text[1:] if text else text


def polish(text: str) -> str:
    text = " ".join(text.split())
    text = text.replace(" ,", ",").replace(",,", ",").replace(" .", ".")
    text = text.replace("..", ".")
    text = re.sub(r"\s+([,.;])", r"\1", text)
    text = " ".join(text.split())
    text = _cap(text)
    if text and not text.endswith((".", "!", "?")):
        text += "."
    return text


def validate_data() -> list:
    problems = []
    for filename, floor in (
        ("actions.txt", 10), ("subjects.txt", 6), ("contexts.txt", 6),
        ("roles.txt", 6), ("places.txt", 6), ("holes.txt", 3),
    ):
        lines = load_txt_file(filename)
        if len(lines) < floor:
            problems.append(f"{filename}: {len(lines)} lines (want >= {floor})")
    return problems


# ---------------------------------------------------------------------------
# Phrase generation
# ---------------------------------------------------------------------------
def build_slots(category: str, spec: dict, pov: str = "first") -> dict:
    actor = "I" if pov == "first" else spec.get("_name", "she")
    poss = "my" if pov == "first" else "her"
    obj = "me" if pov == "first" else spec.get("_name", "her")
    be = "am" if pov == "first" else "is"

    role_word = _pick(load_txt_file("roles.txt"), spec.get("role"))
    slots = {
        "actor": actor, "poss": poss, "obj": obj, "be": be,
        "role": f"{_article(role_word)} {role_word}",
        "subject": _pick(load_txt_file("subjects.txt"), spec.get("subject")),
        "action": _pick(load_txt_file("actions.txt"), spec.get("action")),
        "place": _pick(load_txt_file("places.txt"), spec.get("place")),
        "context": _pick(load_txt_file("contexts.txt"), spec.get("context")),
        "hole": _pick(load_txt_file("holes.txt"), spec.get("hole")),
        "position": _pick(load_txt_file("positions.txt"), spec.get("position")),
        "fluid": _pick(load_txt_file("fluids.txt"), spec.get("fluid")),
        "reaction": _pick(load_txt_file("reactions.txt"), spec.get("reaction")),
        "clothing": _pick(load_txt_file("clothing.txt"), spec.get("clothing")),
        "sound": _pick(load_txt_file("sounds.txt"), spec.get("sound")),
        "toy": _pick(load_txt_file("toys.txt"), spec.get("toy")),
        "number": _pick(load_txt_file("numbers.txt"), spec.get("number")),
        "modifier": _pick(load_txt_file("modifiers.txt"), spec.get("modifier")),
    }
    # derived capitalised variants
    slots["Poss"] = _cap(slots["poss"])
    slots["Position_cap"] = _cap(slots["position"])
    slots["Number_cap"] = _cap(slots["number"])
    slots["Sound_cap"] = _cap(slots["sound"])
    slots["Role_cap"] = _cap(slots["role"])
    return slots


def fill(template: str, slots: dict) -> str:
    """Single-pass substitution so swapped-in text is never re-expanded."""
    pattern = re.compile(r"\{([A-Za-z_]+)\}")

    def repl(match):
        return slots.get(match.group(1), "")

    return pattern.sub(repl, template)


def build_phrase(category: str = "mixed", intensity: int = 2) -> str:
    spec = dict(CATEGORIES.get(category, {}))
    slots = build_slots(category, spec)
    text = fill(random.choice(TEMPLATES), slots)
    if intensity >= 3 and random.random() < 0.5:
        text = text.rstrip(".") + f" -- {fill(random.choice(DEFAULT_DATA['reactions.txt']), slots)}."
    return polish(text)


def generate_phrases(count: int = 50, category: str = "mixed", intensity: int = 2) -> list:
    if not load_txt_file("actions.txt"):
        return ["Error: data/actions.txt is missing or empty."]
    out, seen, tries = [], set(), 0
    guard = max(count * 60, 400)
    keys = list(CATEGORIES)
    while len(out) < count and tries < guard:
        tries += 1
        cat = random.choice(keys) if category == "all" else category
        phrase = build_phrase(cat, intensity)
        if phrase in seen:
            continue
        seen.add(phrase)
        out.append(phrase)
    return out


# ---------------------------------------------------------------------------
# Story generation
# ---------------------------------------------------------------------------
def generate_story(beats: int = 8, theme: str = "random", pov: str = "third",
                   intensity: int = 2) -> str:
    names, titles = load_txt_file("names.txt"), load_txt_file("titles.txt")
    name = random.choice(names) if names else "Ashley"
    title = random.choice(titles) if titles else "Slut"
    persona = f"{title} {name}"

    spec = dict(STORY_THEMES.get(theme, {}))
    spec["_name"] = name

    def slots_for():
        base = dict(spec)
        base["_name"] = name
        return build_slots(theme, base, pov)

    head = slots_for()
    title_line = f"=== {_cap(theme if theme != 'random' else 'Dirty Story')}: {persona} ==="
    parts = [fill(random.choice(STORY_OPENERS), head)]

    for _ in range(max(1, beats)):
        s = slots_for()
        parts.append(fill(random.choice(STORY_BEATS), s))
        if intensity >= 3 and random.random() < 0.35:
            parts.append(fill(random.choice(DEFAULT_DATA["reactions.txt"]), s) + ".")

    parts.append(fill(random.choice(STORY_CLOSERS), slots_for()))
    body = "\n\n".join(polish(p) if p else "" for p in parts)
    return f"{title_line}\n\n{body}\n"


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
def render_phrases(phrases: list, fmt: str) -> str:
    if fmt == "json":
        return json.dumps({"engine": f"Explicit Engine {VERSION}", "count": len(phrases),
                           "phrases": phrases}, indent=2, ensure_ascii=False)
    if fmt == "md":
        return f"# Explicit Engine {VERSION}\n\n" + "\n".join(
            f"{i}. {p}" for i, p in enumerate(phrases, 1)) + "\n"
    if fmt == "html":
        body = "<ol>\n" + "\n".join(f"  <li>{html.escape(p)}</li>" for p in phrases) + "\n</ol>"
        return (HTML_TEMPLATE.replace("__VERSION__", VERSION)
                .replace("__COUNT__", str(len(phrases)))
                .replace("__NOUN__", "phrases").replace("__BODY__", body))
    return "\n".join(f"{i}. {p}" for i, p in enumerate(phrases, 1)) + "\n"


def render_story(story: str, fmt: str) -> str:
    if fmt == "json":
        return json.dumps({"engine": f"Explicit Engine {VERSION}", "story": story},
                          indent=2, ensure_ascii=False)
    if fmt == "md":
        return story.replace("\n\n", "\n\n")
    if fmt == "html":
        paras = "".join(f"<p>{html.escape(p)}</p>\n" for p in story.strip().split("\n\n"))
        body = f'<div class="story">\n{paras}</div>'
        return (HTML_TEMPLATE.replace("__VERSION__", VERSION).replace("__COUNT__", "1")
                .replace("__NOUN__", "story").replace("__BODY__", body))
    return story


def write_out(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------
def get_output_path(default_name: str) -> Path:
    ensure_directories()
    raw = input(f"Filename (default: {default_name}, Enter to accept): ").strip()
    filename = raw or default_name
    if not filename.endswith((".txt", ".md", ".html", ".json")):
        filename += ".txt"
    return DATA_DIR / filename


def show_menu(settings: dict) -> None:
    print("\n" + "=" * 58)
    print(f"MODULAR EXPLICIT PHRASE & STORY ENGINE (v{VERSION})")
    print("=" * 58)
    print(f"1. Generate {settings['default_count']} phrases (intensity {settings['default_intensity']})")
    print(f"2. Generate story ({settings['default_beats']} beats)")
    print("3. Generate a batch of stories")
    print("4. Settings")
    print("5. Data status / validate pools")
    print("6. List categories and themes")
    print("0. Exit")
    print("=" * 58)


def list_reference() -> None:
    print("\nCategories:")
    for key, spec in CATEGORIES.items():
        print(f"  {key:<16} {spec['label']}")
    print("  mixed / all")
    print("\nStory themes:")
    for key, spec in STORY_THEMES.items():
        print(f"  {key:<16} {spec['label']}")
    print("  random")


def data_status() -> None:
    print("\n--- POOL STATUS ---")
    for filename in DEFAULT_DATA:
        lines = load_txt_file(filename)
        flag = "" if len(lines) >= 6 else "  <-- thin"
        print(f"  {filename:<20} {len(lines):>4} lines{flag}")
    problems = validate_data()
    print("\n" + ("All required pools OK." if not problems else "Issues:\n  " + "\n  ".join(problems)))


def settings_menu(settings: dict) -> dict:
    print("\n--- SETTINGS ---")
    print(f"count={settings['default_count']}  beats={settings['default_beats']}  "
          f"intensity={settings['default_intensity']}")
    print(f"phrase file={settings['default_phrase_filename']}  story file={settings['default_story_filename']}")

    raw = input(f"New default count ({settings['default_count']}): ").strip()
    if raw.isdigit() and int(raw) > 0:
        settings["default_count"] = int(raw)
    raw = input(f"New default beats ({settings['default_beats']}): ").strip()
    if raw.isdigit() and int(raw) > 0:
        settings["default_beats"] = int(raw)
    raw = input(f"New intensity 1-3 ({settings['default_intensity']}): ").strip()
    if raw.isdigit() and int(raw) in (1, 2, 3):
        settings["default_intensity"] = int(raw)
    raw = input("New phrase filename: ").strip()
    if raw:
        settings["default_phrase_filename"] = raw if raw.endswith(".txt") else raw + ".txt"
    raw = input("New story filename: ").strip()
    if raw:
        settings["default_story_filename"] = raw if raw.endswith(".txt") else raw + ".txt"
    save_settings(settings)
    print("Saved.")
    return settings


def menu() -> int:
    bootstrap_data()
    settings = load_settings()
    while True:
        show_menu(settings)
        choice = input("Select (0-6): ").strip()
        if choice == "0":
            print("Engine closed.")
            return 0
        if choice == "6":
            list_reference()
            input("\nPress Enter...")
        elif choice == "5":
            data_status()
            input("\nPress Enter...")
        elif choice == "4":
            settings = settings_menu(settings)
            input("\nPress Enter...")
        elif choice == "1":
            cat = input("Category (Enter = mixed): ").strip() or "mixed"
            if cat not in CATEGORIES and cat not in ("mixed", "all"):
                print("Unknown category, using mixed.")
                cat = "mixed"
            path = get_output_path(settings["default_phrase_filename"])
            phrases = generate_phrases(settings["default_count"], cat, settings["default_intensity"])
            write_out(path, render_phrases(phrases, "txt"))
            print(f"\n{len(phrases)} phrases -> {path}\n")
            print("\n".join(f"{i}. {p}" for i, p in enumerate(phrases, 1)))
            input("\nPress Enter...")
        elif choice == "2":
            theme = input("Theme (Enter = random): ").strip() or "random"
            if theme not in STORY_THEMES and theme != "random":
                theme = "random"
            pov = "first" if input("POV: 1 first / 2 third (default 2): ").strip() == "1" else "third"
            path = get_output_path(settings["default_story_filename"])
            story = generate_story(settings["default_beats"], theme, pov, settings["default_intensity"])
            write_out(path, render_story(story, "txt"))
            print(f"\n-> {path}\n")
            print(story)
            input("\nPress Enter...")
        elif choice == "3":
            raw = input("How many stories: ").strip()
            n = int(raw) if raw.isdigit() and int(raw) > 0 else 5
            path = get_output_path("dirty_stories_batch.txt")
            chunks = [generate_story(settings["default_beats"], "random", "third",
                                     settings["default_intensity"]) for _ in range(n)]
            write_out(path, "\n".join(chunks))
            print(f"\n{n} stories -> {path}")
            input("\nPress Enter...")
        else:
            print("Invalid.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="explicit_engine",
                                description="Uncensored modular phrase and story engine.")
    p.add_argument("-n", "--count", type=int, default=None)
    p.add_argument("-c", "--category", default=None,
                   choices=list(CATEGORIES) + ["mixed", "all"])
    p.add_argument("-s", "--story", action="store_true", help="generate a story instead of phrases")
    p.add_argument("-t", "--theme", default="random", choices=list(STORY_THEMES) + ["random"])
    p.add_argument("-b", "--beats", type=int, default=None)
    p.add_argument("--pov", default="third", choices=["first", "third"])
    p.add_argument("-x", "--intensity", type=int, default=None, choices=[1, 2, 3])
    p.add_argument("-o", "--out", default=None)
    p.add_argument("-f", "--format", default=None, choices=["txt", "md", "html", "json"])
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("-i", "--interactive", action="store_true")
    p.add_argument("--status", action="store_true")
    p.add_argument("--list", action="store_true", help="list categories and themes")
    p.add_argument("--version", action="version", version=f"Explicit Engine {VERSION}")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    bootstrap_data()
    if args.seed is not None:
        random.seed(args.seed)
    if args.status:
        data_status()
        return 0
    if args.list:
        list_reference()
        return 0
    if args.interactive or (args.count is None and not args.story and args.out is None
                            and sys.stdin.isatty()):
        try:
            return menu()
        except (KeyboardInterrupt, EOFError):
            print("\nClosed.")
            return 0

    settings = load_settings()
    intensity = args.intensity or settings["default_intensity"]
    fmt = args.format
    if fmt is None:
        suffix = Path(args.out).suffix.lstrip(".").lower() if args.out else ""
        fmt = suffix if suffix in ("txt", "md", "html", "json") else "txt"

    if args.story:
        story = generate_story(args.beats or settings["default_beats"], args.theme,
                               args.pov, intensity)
        content = render_story(story, fmt)
    else:
        phrases = generate_phrases(args.count or settings["default_count"],
                                   args.category or "mixed", intensity)
        content = render_phrases(phrases, fmt)

    if args.out:
        write_out(Path(args.out), content)
        print(f"Saved -> {args.out} ({fmt})")
    else:
        print(content.rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
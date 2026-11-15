#!/usr/bin/env python3
"""
slut_story_generator.py
Creates short filthy stories + vivid dirty sentence generator.
Titles go in front of names (sissy Ashley, prostitute Trina, etc.).
One cock color per story. Expanded dirty_ass. Menu + 50-phrase generator.
Supports .txt and structured .csv export (controlled by settings.py).
"""

import random
import sys
import csv
import os
from datetime import datetime

# Import settings (with safe defaults if file is missing)
try:
    from settings import (
        SAVE_TXT,
        SAVE_CSV,
        DEFAULT_STORY_COUNT,
        DEFAULT_SENTENCE_COUNT,
        OUTPUT_FOLDER,
        CSV_ENCODING,
    )
except ImportError:
    SAVE_TXT = True
    SAVE_CSV = False
    DEFAULT_STORY_COUNT = 5
    DEFAULT_SENTENCE_COUNT = 50
    OUTPUT_FOLDER = ""
    CSV_ENCODING = "utf-8"

# ============================================================
# 50 GIRL NAMES
# ============================================================
NAMES = [
    "Ashley", "Trina", "Chloe", "Brittany", "Jessica",
    "Tiffany", "Amber", "Samantha", "Destiny", "Candy",
    "Lexi", "Chanel", "Nikki", "Savannah", "Zoe",
    "Britney", "Crystal", "Diamond", "Raven", "Jade",
    "Scarlett", "Vanessa", "Monica", "Heather", "Kelly",
    "Megan", "Nicole", "Stephanie", "Amanda", "Jennifer",
    "Michelle", "Kimberly", "Angela", "Melissa", "Rachel",
    "Lauren", "Emily", "Hannah", "Olivia", "Sophia",
    "Ava", "Isabella", "Mia", "Charlotte", "Amelia",
    "Harper", "Evelyn", "Abigail", "Ella", "Ruby"
]

# ============================================================
# TITLES (placed in front of the name)
# ============================================================
TITLES = [
    "sissy",
    "bimbo",
    "prostitute",
    "mistress",
    "transwoman",
    "cumdump",
    "whore",
    "slut",
    "cumslut",
    "fuckpet",
    "cumtoilet",
    "cock-sleeve",
    "breeding-whore",
    "motel slut",
    "gloryhole regular",
    "anal slut",
    "throat slut",
    "public whore",
    "street whore",
    "used whore",
    "sissy whore",
    "bimbo slut",
    "trans whore",
    "gaping slut",
    "desperate cumdump"
]

# ============================================================
# ROLES
# ============================================================
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
    "shameless sissy slut",
    "needy bimbo cumslut",
    "cock-hungry street whore",
    "willing public-use slut",
    "drooling throat toy",
    "greedy little cumdump",
    "shameless anal whore",
    "spoiled motel slut",
    "sissy bimbo",
    "used-up whore",
    "public-use whore",
    "toilet whore",
    "cum sponge",
    "sissy toy",
    "bimbo cumslut"
]

# ============================================================
# COCK DESCRIPTIONS – BLACK ONLY
# ============================================================
BLACK_COCKS = [
    "that massive big black cock",
    "that throbbing big black cock",
    "that heavy black shaft",
    "an enormous black dick",
    "that monster big black cock",
    "a black cock thicker than her wrist",
    "the biggest big black cock she could take",
    "a slick ebony shaft",
    "a black cock with a thick vein running down the shaft",
    "that heavy-hanging black dick",
    "that thick black cock",
    "a heavy ebony shaft",
    "a thick black shaft slick with spit",
    "eight thick black cocks",
    "a circle of heavy black dicks",
    "a fat uncut big black cock",
    "two fat black cocks at once",
    "a train of anonymous black dicks",
    "that long thick black dick",
    "a fat-headed big black cock",
    "that broad black cock",
    "a massive black dick",
    "that thick black dick"
]

# ============================================================
# COCK DESCRIPTIONS – WHITE ONLY
# ============================================================
WHITE_COCKS = [
    "that massive big white cock",
    "that throbbing big white cock",
    "that heavy white shaft",
    "an enormous white dick",
    "that monster big white cock",
    "a white cock thicker than her wrist",
    "the biggest big white cock she could take",
    "a long pale white-boy cock",
    "a fat-headed big white cock",
    "that heavy-hanging white dick",
    "that thick big white cock",
    "a pale thick white dick",
    "a thick white shaft slick with spit",
    "eight thick white cocks",
    "a circle of heavy white dicks",
    "a fat uncut big white cock",
    "two fat white cocks at once",
    "a train of anonymous white dicks",
    "that long thick white dick",
    "that broad white cock",
    "a massive white dick",
    "that thick white dick"
]

# ============================================================
# COCK / DICK TYPES
# ============================================================
COCK_TYPES = [
    "big black cock", "big white cock", "thick cock", "hard cock",
    "heavy cock", "throbbing cock", "massive cock", "black shaft",
    "ebony cock", "pale cock", "dick", "dicks", "thick dick",
    "hard dick", "heavy dick", "throbbing dick", "massive dick",
    "fat dick", "long dick", "fat cock", "long cock"
]

# ============================================================
# PLACES
# ============================================================
PLACES = [
    "the grimy rest-stop bathroom stall",
    "the back-alley gloryhole room",
    "the truck-stop parking lot at midnight",
    "the party room with birthday cake and cupcakes",
    "the public restroom backroom",
    "the truck-stop gloryhole",
    "the rest-stop bathroom",
    "the club bathroom stall",
    "the alley behind the bar",
    "the park bench",
    "the stairwell",
    "the laundromat",
    "the motel room",
    "the gym sauna",
    "the truck cab",
    "the balcony",
    "the back room",
    "the parking garage",
    "the picnic table",
    "the changing room",
    "the doorway after closing",
    "the bare mattress on the floor",
    "the house party",
    "the bushes at the park edge",
    "under the bridge",
    "the shower block",
    "the counter of a closed shop",
    "the taxi back seat",
    "the cheap hotel corridor",
    "the football club locker room",
    "the private room at the back of the club",
    "the quiet motel room with the rumpled sheets",
    "the locked dressing room after the party",
    "the dim corner of the adult club",
    "Room 1408 of The Velvet Crown Hotel",
    "a filthy motel room",
    "the gloryhole booth",
    "the back of a van"
]

# ============================================================
# CLOTHING
# ============================================================
CLOTHING = [
    "wearing only a collar and fishnets",
    "naked except for spiked heels and a leash",
    "wearing a slutty maid outfit covered in jizz",
    "in crotchless lingerie and whorish red lipstick",
    "in a tiny pink bikini that barely covered anything",
    "wearing nothing but thigh-highs and smeared makeup",
    "in a cheap micro-skirt and no panties",
    "dressed like a street whore in fishnets and a crop top",
    "in a collar, heels, and nothing else",
    "wearing a used, cum-stained babydoll",
    "in open-crotch pantyhose and a push-up bra",
    "wearing only red lipstick and a plug"
]

# ============================================================
# POSITIONS
# ============================================================
POSITIONS = [
    "doggy with her face pushed into the dirt",
    "on her back, legs over his shoulders",
    "reverse cowgirl with her ass jiggling",
    "cowgirl with her hands on his chest",
    "flat on her belly",
    "folded in half",
    "standing against the wall",
    "on her knees with her hands behind her back",
    "upside down",
    "spread-eagle",
    "spooned from behind",
    "in a deep squat",
    "bent over the bench with her heels lifted",
    "tied to the rail",
    "holding her own ankles",
    "in a headlock on the cock",
    "bent over the sink",
    "braced on the tiles",
    "straddling him backwards",
    "pressed to the wall with her cheek flat",
    "on her knees with her hands on the mattress",
    "bent over with her cheek against the sheets",
    "straddling him with her hips rolling slowly",
    "on her back with her legs wrapped around him",
    "standing against the wall with her skirt hiked up",
    "upside down with her legs forced back over her head",
    "on all fours with her ass high and face down",
    "turned upside down and throated",
    "turned upside down and face fucked"
]

# ============================================================
# PASSIVE ACTIONS
# ============================================================
PASSIVE = [
    "got face fucked by",
    "got throat fucked by",
    "got dp'd by",
    "got spit roasted by",
    "got gangbanged by",
    "got gang fucked by",
    "got her asshole wrecked by",
    "got her ass reamed by",
    "got creampied by",
    "got bred by",
    "got stretched out by",
    "got pounded by",
    "got slapped and spat on by",
    "got her throat stretched by",
    "got used by",
    "got her holes filled by",
    "got her mouth used by",
    "got gaped wide by",
    "got her tits slapped by",
    "got passed around by",
    "got drilled by",
    "got her ass eaten by",
    "got her ass stretched by",
    "got her throat filled by",
    "got pounded hard by",
    "got used all night by",
    "got her ass fucked by",
    "got ass fucked by",
    "was face fucked by",
    "got fucked hard by",
    "got fucked slowly by",
    "got her gaping asshole filled by",
    "got her face covered in cum by",
    "got her throat used like a hole by",
    "got turned upside down and throated by",
    "got turned upside down and face fucked by",
    "got gagging on cock from"
]

# ============================================================
# DIRTY ASS – expanded
# ============================================================
DIRTY_ASS = [
    "her gaping asshole",
    "her stretched butthole",
    "her loose anal hole",
    "her weeping ass-tunnel",
    "her dripping asshole",
    "her stretched out gaping asshole",
    "her gaped and loose asshole",
    "her open, cum-leaking hole",
    "her ruined, gaping ass",
    "her slick, stretched hole",
    "her ruined, cum-dripping asshole",
    "her wide-open, spit-shined asshole",
    "her permanently stretched fuckhole",
    "her loose, winking asshole",
    "her cum-flooded ass-tunnel",
    "her swollen, gaping butt-hole",
    "her used-up, drooling asshole",
    "her wrecked, open anal ring",
    "her soft, ruined asshole",
    "her deep, cum-soaked ass",
    "her aching, stretched-out hole",
    "her messy, gaping fuck-tunnel",
    "her spit-slick, open asshole",
    "her bruised, cum-leaking hole",
    "her floppy, used asshole",
    "her stretched out gaping asshole that winked and drooled cum",
    "her ruined, wide-open asshole that stayed gaped",
    "her soft, permanently stretched fuck-tunnel",
    "her glossy, swollen, gaping hole",
    "her loose, cum-leaking asshole that wouldn't close",
    "her wrecked anal ring that pulsed open",
    "her deep, ruined ass-tunnel dripping thick cum",
    "her open, spit-shined, gaping asshole"
]

# ============================================================
# FLUIDS
# ============================================================
FLUIDS = [
    "thick warm jizz",
    "frothy cum-drool mixture",
    "sticky white ropes",
    "warm streaks of cum",
    "slick drops of precum",
    "a shiny mix of spit and lube",
    "thick ropes running down her thighs",
    "heavy loads of cum",
    "thick semen",
    "spit and cum mixed together",
    "long ropes of cum",
    "a flood of warm cum",
    "sticky white cum",
    "thick cum that dripped from her chin"
]

# ============================================================
# REACTIONS
# ============================================================
REACTIONS = [
    "Her makeup ran down her face and she didn't care.",
    "Cum dripped out of her onto the floor.",
    "Her asshole was gaping and winking.",
    "Everyone watched and she loved every second.",
    "She was dripping and shaking.",
    "They pulled out and she pushed the cum back out.",
    "She licked her lips and asked for more.",
    "Her legs gave out and she just lay there.",
    "She could taste herself on their cocks.",
    "Nobody said a word, they just kept going.",
    "Her throat was raw and she still wanted it.",
    "She spat the load back out and grinned.",
    "She wiped her mouth, smiled, and asked who was next.",
    "Her legs trembled, but she pulled him back toward her.",
    "She caught her breath and grinned at the mess they had made.",
    "She stayed close, flushed and eager for another round.",
    "She caught her breath after getting her ass fucked and asked him to keep going.",
    "She wiped her mouth after the face fucking and pulled him back toward her.",
    "Her thighs were still shaking, but she kept fucking him and grinning.",
    "She wanted to get fucked again before the night was over.",
    "She wept tears of absolute degradation.",
    "She choked and gasped for air as jizz flooded her throat.",
    "She shuddered as her gaping asshole pulsed uncontrollably.",
    "Spit ran down her face while she gagged.",
    "Her whorish red lipstick was completely destroyed.",
    "Cum covered her face, filled her mouth, and leaked from her gaping asshole."
]

# ============================================================
# SMELLS
# ============================================================
SMELLS = [
    "stale beer and hot cum",
    "sweat and heavy musk",
    "unwashed cock and leaked jizz",
    "truck-stop bathroom cleaner and fresh cum",
    "spicy cologne and sweat",
    "spilled beer and perfume",
    "warm skin and clean sheets",
    "cheap perfume and sex",
    "musk and spit"
]

# ============================================================
# REASONS
# ============================================================
REASONS = [
    "getting completely used and filled with jizz",
    "serving as a public cumdump for strangers",
    "absolute humiliation and anal stretching",
    "the thrill of being watched",
    "a night of shameless fun",
    "her own appetite for trouble",
    "being turned into a used toy",
    "the camera rolling while she took every cock"
]

# ============================================================
# TERMS
# ============================================================
TERMS = [
    "brutal gangbang marathon",
    "truck-stop cum-draining session",
    "public bukkake and cumswapping ritual",
    "slow, crowded rotation",
    "messy group turn",
    "long line taking turns",
    "packed bukkake finish",
    "gangbang face fucking",
    "upside-down throat session",
    "filthy motel gangbang"
]

# ============================================================
# EXTRA FILTH
# ============================================================
EXTRA_FILTH = [
    "Spit ran down her face the whole time.",
    "They slapped her face with their heavy cocks between thrusts.",
    "Her crotchless lingerie was soaked and ruined.",
    "The camera captured every gag and every load.",
    "They took turns dumping cum on her face, in her mouth, and deep in her gaped asshole.",
    "She watched the cocks disappear into her throat while hanging upside down.",
    "Thick ropes of cum painted her face while more leaked from her stretched out gaping asshole.",
    "They kept her upside down and used her throat like a hole.",
    "One after another they face-fucked her until spit and cum covered everything.",
    "Her makeup was a complete mess of spit, tears, and semen.",
    "She was gagging on cock the entire time.",
    "They turned her upside down and throated her until she choked.",
    "They turned her upside down and face fucked her while she watched.",
    "She held her mouth open like a bukkake bowl while dozens of men unloaded on her face and tongue.",
    "Everyone came on her face and in her open mouth; she kept it wide like a good cock-craving slut and swallowed every drop.",
    "Her face was completely painted white and her mouth overflowed with cum that she drank down.",
    "She sucked every dick first, then knelt with her tongue out and collected load after load in her bukkake bowl.",
    "Fifty or more loads hit her cheeks, forehead, and open mouth until she looked like a glazed cumdump.",
    "She stayed perfectly still, mouth open, and took every rope like the desperate slut she was.",
    "Cum ran into her eyes and down her chin while she kept her mouth open as their collective bukkake bowl.",
    "By the end her face was a thick mask of cum and she had swallowed so many loads her stomach felt heavy.",
    "She gagged hard every time a cock bottomed out in her throat, spit pouring down her chin.",
    "He face-fucked her until she gagged and a mouthful of spit and bile came up around his cock.",
    "She puked a little when the cock punched the back of her throat, but he kept fucking her face through it.",
    "Spit and throat slime poured out of her as she gagged and nearly threw up on his cock.",
    "He didn’t stop when she started heaving — he used the mess as extra lube and kept face-fucking her.",
    "Her stretched out gaping asshole winked and drooled cum long after they pulled out.",
    "Her asshole stayed wide open, soft, and continuously leaking.",
    "Her gaped and loose asshole stayed open like a wet mouth, showing everyone how thoroughly it had been used."
]

# ============================================================
# STORY GENERATOR (one color per story)
# ============================================================
def generate_story():
    """Return a dict with structured fields + full story text."""
    title = random.choice(TITLES)
    name = random.choice(NAMES)
    full_name = f"{title} {name}"
    role = random.choice(ROLES)
    place = random.choice(PLACES)
    clothing = random.choice(CLOTHING)
    position = random.choice(POSITIONS)
    passive = random.choice(PASSIVE)
    fluid = random.choice(FLUIDS)
    dirty_ass = random.choice(DIRTY_ASS)
    reaction = random.choice(REACTIONS)
    smell = random.choice(SMELLS)
    reason = random.choice(REASONS)
    term = random.choice(TERMS)
    extra = random.choice(EXTRA_FILTH)
    extra2 = random.choice(EXTRA_FILTH)

    # One color only for the whole story
    if random.random() < 0.55:
        cock_color = "black"
        cock1 = random.choice(BLACK_COCKS)
        cock2 = random.choice(BLACK_COCKS)
    else:
        cock_color = "white"
        cock1 = random.choice(WHITE_COCKS)
        cock2 = random.choice(WHITE_COCKS)

    full_text = (
        f"{full_name} showed up at {place} {clothing}, already looking like a {role}. "
        f"The air smelled of {smell}. "
        f"They put her {position} and the {term} started. "
        f"She {passive} {cock1} while {cock2} waited for its turn. "
        f"{extra} "
        f"They filled her mouth, covered her face, and pumped {fluid} into {dirty_ass}. "
        f"{extra2} "
        f"{reaction} "
        f"By the end she was nothing but a used, cum-covered {role} who had come for {reason}."
    )
    full_text = " ".join(full_text.split())

    return {
        "title": title,
        "name": name,
        "full_name": full_name,
        "role": role,
        "place": place,
        "clothing": clothing,
        "position": position,
        "cock_color": cock_color,
        "cock1": cock1,
        "cock2": cock2,
        "dirty_ass": dirty_ass,
        "fluid": fluid,
        "term": term,
        "full_story": full_text,
    }


def generate_multiple_stories(n=None):
    """Generate n stories. Returns (list_of_dicts, formatted_text)."""
    if n is None:
        n = DEFAULT_STORY_COUNT
    stories_data = [generate_story() for _ in range(n)]
    formatted = "\n".join(
        f"--- Story {i+1} ---\n{s['full_story']}\n" for i, s in enumerate(stories_data)
    )
    return stories_data, formatted


# ============================================================
# DIRTY SENTENCE GENERATOR – 50 vivid first-person phrases
# ============================================================
def generate_dirty_sentences(n=50):
    templates = [
        "I gagged like a worthless sissy whore as that massive big black cock slammed down my throat, spit and precum pouring out while I deepthroated it until my eyes watered.",
        "I loved gagging on that big black cock until spit ran down my chin.",
        "I couldn't get enough of that thick black cock slamming down my throat.",
        "I loved feeling every inch of that big black cock stretching my lips.",
        "That big black cock had me coming back to get my face wrecked more.",
        "I loved taking my time choking on that massive big black cock.",
        "I wanted more of that delicious black thickness ruining my throat.",
        "I loved the way he face fucked me with that big black cock.",
        "That cock was impossible to forget as it gagged me like a whore.",
        "I loved every second of being his throat slut for that big black cock.",
        "I was a pathetic hole gagging on that big black cock.",
        "My mouth was just a fucktoy for that big black cock to destroy.",
        "I drooled like a cheap slut while that big black cock rammed my face.",
        "Tears streamed down as that big black cock choked me out.",
        "I loved being used as a throat toilet for that big black cock.",
        "That big black cock turned my face into a messy cumdump.",
        "I begged for that big black cock to fuck my throat harder.",
        "I was nothing but a dirty face whore taking that big black cock.",
        "My makeup smeared as that big black cock wrecked my mouth.",
        "I loved the taste of that big black cock filling my throat.",
        "That thick black cock made me retch and spit like a prostitute.",
        "I couldn't stop sucking that big black cock even while gagging.",
        "I loved how that big black cock dominated my entire head.",
        "Every inch of that big black cock disappeared down my throat.",
        "I was addicted to getting face fucked by that big black cock.",
        "That big black cock stretched my jaw until it ached.",
        "I loved feeling that big black cock pulse against my tonsils.",
        "He used my face like a cheap toy with that big black cock.",
        "I was a worthless sissy choking on that big black cock.",
        "That big black cock made me puke but I kept sucking.",
        "I loved the way that big black cock slapped my cheeks.",
        "My throat burned from that big black cock but I wanted more.",
        "I wanted that big black cock to ruin my face forever.",
        "That big black cock had me on my knees like a good little slut.",
        "I loved swallowing around that big black cock in my throat.",
        "Every thrust of that big black cock made me a bigger whore.",
        "I was his personal face fuck hole for that big black cock.",
        "That big black cock coated my tongue with thick pre-cum.",
        "I loved being degraded by that massive big black cock in my mouth.",
        "Spit and tears mixed as that big black cock used my face.",
        "I couldn't get enough of choking on that big black cock.",
        "That big black cock turned me into a drooling mess.",
        "I loved how deep that big black cock went down my throat.",
        "He grabbed my hair and face fucked me with that big black cock.",
        "I was just a mouth for that big black cock to destroy.",
        "That big black cock made me forget I had any pride.",
        "I loved the musky smell of that big black cock as it fucked my face.",
        "My throat was raw from that big black cock but I craved more.",
        "I begged him to face fuck me like a slut with that big black cock.",
        "That big black cock was the only thing I lived for in my mouth.",
        "I loved being a filthy throat whore for that big black cock.",
        "I loved taking that big black cock deep in my ass.",
        "I couldn't get enough of that thick black cock stretching my hole.",
        "I loved feeling every inch of that big black cock in my ass.",
        "That big black cock had me coming back to get my ass wrecked more.",
        "I loved taking my time bouncing on that massive big black cock.",
        "I wanted more of that delicious black thickness filling my ass.",
        "I loved the way he fucked my ass with that big black cock.",
        "That cock was impossible to forget as it split my hole open.",
        "I loved every second of being his anal slut for that big black cock.",
        "I was a pathetic hole taking that big black cock in my ass.",
        "My ass was just a fucktoy for that big black cock to destroy.",
        "I moaned like a cheap whore while that big black cock rammed my ass.",
        "Tears came as that big black cock stretched my tight hole.",
        "I loved being used as an ass toilet for that big black cock.",
        "That big black cock turned my hole into a messy cumdump.",
        "I begged for that big black cock to fuck my ass harder.",
        "I was nothing but a dirty ass whore taking that big black cock.",
        "My hole gaped as that big black cock wrecked my ass.",
        "I loved the feeling of that big black cock filling my guts.",
        "That thick black cock made me squirt like a prostitute.",
        "I couldn't stop riding that big black cock even while it hurt.",
        "I loved how that big black cock dominated my entire ass.",
        "Every inch of that big black cock disappeared in my hole.",
        "I was addicted to getting ass fucked by that big black cock.",
        "That big black cock stretched my ass until it burned.",
        "I loved feeling that big black cock pulse inside my ass.",
        "He used my ass like a cheap toy with that big black cock.",
        "I was a worthless sissy taking that big black cock in my hole.",
        "That big black cock made me leak but I kept pushing back.",
        "I loved the way that big black cock slapped my ass cheeks.",
        "My hole was sore from that big black cock but I wanted more.",
        "I wanted that big black cock to ruin my ass forever.",
        "That big black cock had me bent over like a good little slut.",
        "I loved clenching around that big black cock in my ass.",
        "Every thrust of that big black cock made me a bigger whore.",
        "I was his personal ass fuck hole for that big black cock.",
        "That big black cock coated my insides with thick pre-cum.",
        "I loved being degraded by that massive big black cock in my hole.",
        "Lube and spit mixed as that big black cock used my ass.",
        "I couldn't get enough of taking that big black cock in my ass.",
        "That big black cock turned me into a gaping mess.",
        "I loved how deep that big black cock went in my ass.",
        "He grabbed my hips and ass fucked me with that big black cock.",
        "I was just a hole for that big black cock to destroy.",
        "That big black cock made me forget I had any dignity.",
        "I loved the musky smell of that big black cock as it fucked my ass.",
        "My ass was raw from that big black cock but I craved more.",
        "I begged him to ass fuck me like a slut with that big black cock.",
        "That big black cock was the only thing I lived for in my hole.",
        "I loved being a filthy ass whore for that big black cock.",
        "I loved when that big black cock exploded all over my face.",
        "I couldn't get enough of that thick black cock shooting on me.",
        "I loved feeling every rope of that big black cock cum.",
        "That big black cock had me coming back for more facials.",
        "I loved taking my time licking that massive big black cock cum.",
        "I wanted more of that delicious black thickness covering me.",
        "I loved the way he came on me with that big black cock.",
        "That cock was impossible to forget as it painted my face.",
        "I loved every second of being his cum slut for that big black cock.",
        "I was a pathetic canvas for that big black cock to unload.",
        "My face was just a target for that big black cock to destroy.",
        "I moaned like a cheap whore while that big black cock came on me.",
        "Tears mixed with cum as that big black cock shot on my face.",
        "I loved being used as a cumdump for that big black cock.",
        "That big black cock turned my face into a messy load.",
        "I begged for that big black cock to cum on me harder.",
        "I was nothing but a dirty cum whore taking that big black cock.",
        "My skin glistened as that big black cock wrecked my face with cum.",
        "I loved the taste of that big black cock shooting in my mouth.",
        "That thick black cock made me swallow like a prostitute.",
        "I couldn't stop licking that big black cock even while it came.",
        "I loved how that big black cock dominated me with its load.",
        "Every spurt of that big black cock covered my body.",
        "I was addicted to getting painted by that big black cock.",
        "That big black cock stretched my limits with its huge load.",
        "I loved feeling that big black cock pulse as it came.",
        "He used my body like a cheap toy with that big black cock cum.",
        "I was a worthless sissy covered in that big black cock.",
        "That big black cock made me drip but I kept begging.",
        "I loved the way that big black cock glazed my tits.",
        "My face was sticky from that big black cock but I wanted more.",
        "I wanted that big black cock to ruin me with its cum forever.",
        "That big black cock had me kneeling like a good little slut.",
        "I loved tasting that big black cock as it exploded.",
        "Every shot of that big black cock made me a bigger whore.",
        "I was his personal cum hole for that big black cock.",
        "That big black cock coated me with thick white ropes.",
        "I loved being degraded by that massive big black cock load.",
        "Cum and spit mixed as that big black cock used me.",
        "I couldn't get enough of that big black cock shooting on me.",
        "That big black cock turned me into a dripping mess.",
        "I loved how much that big black cock came on my face.",
        "He grabbed my head and came with that big black cock.",
        "I was just a target for that big black cock to destroy.",
        "That big black cock made me forget I had any pride.",
        "I loved the musky smell of that big black cock as it came.",
        "My body was covered from that big black cock but I craved more.",
        "I begged him to cum on me like a slut with that big black cock.",
        "That big black cock was the only thing I lived for on my skin.",
        "I loved being a filthy cum whore for that big black cock.",
        "They turned me upside down and throated me with that big black cock until I choked.",
        "They turned me upside down and face fucked me while I watched every inch disappear.",
        "I was gagging on cock the whole time, spit running down my face.",
        "My stretched out gaping asshole leaked thick cum after that big black cock pulled out.",
        "I loved feeling my gaping asshole wink and drip after he finished with me.",
        "Spit ran down my chin while I gagged on that massive big black cock.",
        "I stayed upside down with my legs forced back while they used my throat like a hole.",
        "Cum covered my face, filled my mouth, and leaked from my stretched out gaping asshole.",
        "I was a worthless sissy whore getting my face and ass wrecked by that big black cock.",
        "My whorish red lipstick was completely destroyed by the constant face fucking.",
        "I held my mouth open like a bukkake bowl while fifty men lined up and unloaded on my face and tongue.",
        "Everyone came on my face and in my open mouth; I kept it wide like a good cock-craving slut and swallowed every single drop.",
        "There were over sixty loads. My face was completely painted white and my mouth was an overflowing bowl of cum that I drank down without spilling.",
        "I sucked every dick in the room first, then knelt with my tongue out and let them all finish on my face and in my bukkake bowl.",
        "Load after load hit my cheeks, forehead, and open mouth until I looked like a glazed cumdump. I swallowed the whole bowl when they were done.",
        "Fifty to eighty cocks used my face as a target. I stayed perfectly still, mouth open, and took every rope like the desperate slut I was.",
        "My face was dripping. Cum ran into my eyes and down my chin while I kept my mouth open as their collective bukkake bowl.",
        "I sucked them all hard first so the loads would be bigger, then collected everything in my mouth and on my face before swallowing the entire mess.",
        "They treated my open mouth like a communal cum bowl. One after another they stepped up, stroked, and dumped straight onto my tongue.",
        "By the end my face was a thick mask of cum and I had swallowed so many loads my stomach felt heavy. I still licked the last drops off my lips.",
        "My stretched out gaping asshole winked and drooled cum long after he pulled out.",
        "That cock left my asshole ruined — wide open, soft, and continuously leaking.",
        "My gaped and loose asshole stayed open like a wet mouth, showing everyone how thoroughly it had been used.",
        "I could feel cool air inside my stretched out gaping asshole; it wouldn’t close.",
        "Cum poured out of my gaping asshole in thick strands every time I clenched.",
        "My asshole was so stretched it looked permanently open, red, and shiny with spit and cum.",
        "They kept my cheeks spread so everyone could stare at my wrecked, gaping hole.",
        "My stretched out gaping asshole pulsed and fluttered, still trying to close around nothing.",
        "After they finished, my asshole stayed wide and loose, a clear invitation for the next cock.",
        "I reached back and felt how open I was — my fingers slid into my stretched out gaping asshole with almost no resistance.",
        "Thick cum leaked from my gaped hole onto the floor in slow, heavy drops.",
        "My hole was a glossy, swollen, permanently stretched mess by the time they were done.",
        "I pushed out and showed them my stretched out gaping asshole, letting the cum run freely.",
        "He face-fucked me with that big black cock until spit ran in sheets down my chin.",
        "I gagged hard every time that big white cock bottomed out in my throat.",
        "My eyes watered and my mascara ran while he used my throat like a pussy.",
        "Spit bubbles formed at the corners of my mouth as I gagged on his thick cock.",
        "He held my head still and face-fucked me through the gagging until I was a drooling mess.",
        "I choked and gagged but he never slowed down — he just kept driving that cock deeper.",
        "Thick strings of spit connected my lips to his cock every time he pulled back.",
        "My throat made wet, ugly sounds while he face-fucked me without mercy.",
        "I was gagging so hard my whole body jerked, but I still kept my mouth open for more.",
        "He slapped his cock against my tongue between thrusts just to watch me drool and gasp.",
        "He face-fucked me so deep I gagged until a mouthful of spit and bile came up around his cock.",
        "I puked a little when that big black cock punched the back of my throat, but he kept fucking my face through it.",
        "Spit and throat slime poured out of me as I gagged and nearly threw up on his cock.",
        "He didn’t stop when I started heaving — he used the mess as extra lube and kept face-fucking me.",
        "I coughed up thick spit and a bit of puke while he held my head and forced his cock back in.",
        "My throat rebelled and I gagged hard enough to bring something up, yet I still swallowed around his cock afterward.",
        "He pulled out just long enough for me to spit the mess onto the floor, then shoved back in and continued face-fucking me.",
        "I was a ruined, puking, drooling face-fuck hole by the time he finished with my throat.",
        "I sucked every cock first, then knelt as their bukkake bowl while fifty loads painted my face and filled my mouth. I swallowed everything.",
        "My stretched out gaping asshole leaked the whole time they were covering my face in cum.",
        "They face-fucked me until I gagged and nearly puked, then made me open my mouth again so the next men could use me as a cum bowl.",
        "By the end my face was a thick mask of cum, my throat was raw from gagging, and my asshole was still gaping open and dripping."
    ]

    selected = random.sample(templates, min(n, len(templates)))
    while len(selected) < n:
        selected.append(random.choice(templates))

    result = []
    for i, phrase in enumerate(selected[:n], 1):
        result.append(f"{i}. {phrase}")
    return "\n".join(result)


# ============================================================
# SAVE HELPERS
# ============================================================
def _make_filename(prefix: str, ext: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"{prefix}_{timestamp}.{ext}"
    if OUTPUT_FOLDER:
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        return os.path.join(OUTPUT_FOLDER, name)
    return name


def save_to_txt(content: str, prefix: str) -> str:
    """Save plain text content to a timestamped .txt file."""
    filename = _make_filename(prefix, "txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename


def save_stories_to_csv(stories_data: list[dict], prefix: str = "slut_stories") -> str:
    """Save structured story data to CSV."""
    filename = _make_filename(prefix, "csv")
    fieldnames = [
        "title", "name", "full_name", "role", "place", "clothing",
        "position", "cock_color", "cock1", "cock2", "dirty_ass",
        "fluid", "term", "full_story"
    ]
    with open(filename, "w", newline="", encoding=CSV_ENCODING) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in stories_data:
            writer.writerow(row)
    return filename


def save_sentences_to_csv(sentences_text: str, prefix: str = "dirty_sentences") -> str:
    """Save numbered dirty sentences to CSV."""
    filename = _make_filename(prefix, "csv")
    lines = [line.strip() for line in sentences_text.splitlines() if line.strip()]
    with open(filename, "w", newline="", encoding=CSV_ENCODING) as f:
        writer = csv.writer(f)
        writer.writerow(["number", "phrase"])
        for line in lines:
            if ". " in line:
                num, phrase = line.split(". ", 1)
                writer.writerow([num, phrase])
            else:
                writer.writerow(["", line])
    return filename


def save_outputs(stories_data=None, stories_text=None, sentences_text=None):
    """Save according to settings. Returns list of saved filenames."""
    saved = []
    if stories_text and SAVE_TXT:
        saved.append(save_to_txt(stories_text, "slut_stories"))
    if stories_data and SAVE_CSV:
        saved.append(save_stories_to_csv(stories_data))
    if sentences_text and SAVE_TXT:
        saved.append(save_to_txt(sentences_text, "dirty_sentences"))
    if sentences_text and SAVE_CSV:
        saved.append(save_sentences_to_csv(sentences_text))
    return saved


# ============================================================
# MENU
# ============================================================
def show_menu():
    csv_status = "ON" if SAVE_CSV else "OFF"
    txt_status = "ON" if SAVE_TXT else "OFF"
    print("\n" + "=" * 60)
    print("  SLUT STORY GENERATOR")
    print("=" * 60)
    print(f"1. Generate short filthy stories ({DEFAULT_STORY_COUNT})")
    print(f"2. Generate {DEFAULT_SENTENCE_COUNT} dirty first-person sentences")
    print("3. Generate both")
    print("4. Exit")
    print("-" * 60)
    print(f"  TXT saving: {txt_status}   |   CSV saving: {csv_status}")
    print("  (edit settings.py to change)")
    print("=" * 60)


def main():
    while True:
        show_menu()
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            stories_data, stories_text = generate_multiple_stories()
            print("\n" + stories_text)
            saved = save_outputs(stories_data=stories_data, stories_text=stories_text)
            for f in saved:
                print(f"[Saved to {f}]")

        elif choice == "2":
            sentences = generate_dirty_sentences(DEFAULT_SENTENCE_COUNT)
            print("\n--- Dirty Sentences ---\n")
            print(sentences)
            saved = save_outputs(sentences_text=sentences)
            for f in saved:
                print(f"[Saved to {f}]")

        elif choice == "3":
            stories_data, stories_text = generate_multiple_stories()
            sentences = generate_dirty_sentences(DEFAULT_SENTENCE_COUNT)
            print("\n" + stories_text)
            print("\n--- Dirty Sentences ---\n")
            print(sentences)
            saved = save_outputs(
                stories_data=stories_data,
                stories_text=stories_text,
                sentences_text=sentences,
            )
            for f in saved:
                print(f"[Saved to {f}]")

        elif choice == "4":
            print("\nBye, you filthy thing.")
            sys.exit(0)
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()

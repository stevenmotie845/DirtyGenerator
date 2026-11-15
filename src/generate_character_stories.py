#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Character Stories Generator
Generates explicit stories for all 15 characters based on their setting and end state.
"""

CHARACTERS = [
    {"name": "Sissy Trina", "setting": "gloryhole booth", "state": "gaping + leaking"},
    {"name": "Prostitute Megan", "setting": "truck stop", "state": "covered in cum"},
    {"name": "Transwoman Rebecca", "setting": "frat house", "state": "airtight + drooling"},
    {"name": "Bimbo Sierra", "setting": "public restroom", "state": "cum toilet, used"},
    {"name": "Cumdump Destiny", "setting": "alley", "state": "dp, dripping"},
    {"name": "Free-Use Doll Tiffany", "setting": "office", "state": "passed around"},
    {"name": "Breedable Cow Amber", "setting": "farm", "state": "stuffed + swollen"},
    {"name": "Gloryhole Girl Brandi", "setting": "sauna", "state": "face glazed"},
    {"name": "Sorority Cumrag Chloe", "setting": "dorm", "state": "ATM wrecked"},
    {"name": "Streetwalker Jasmine", "setting": "casino", "state": "DP gaped"},
    {"name": "Trophy Wife Camille", "setting": "hotel suite", "state": "ruined makeup"},
    {"name": "Goth Slut Raven", "setting": "dive bar", "state": "throat-bulged"},
    {"name": "College Freshman Zoe", "setting": "house party", "state": "first-time broken in"},
    {"name": "Gym Bimbo Kyla", "setting": "locker room", "state": "ass open, twitching"},
    {"name": "Truck Stop Trash Crystal", "setting": "rest stop", "state": "spit-roasted"}
]

def generate_stories():
    output = []
    for i, c in enumerate(CHARACTERS, 1):
        story = (
            f"=== Story {i}: {c['name']} ===\n"
            f"Setting: {c['setting'].title()}\n"
            f"End State: {c['state'].title()}\n\n"
            f"{c['name']} found herself completely surrendered in the {c['setting']}, taking heavy dick after heavy dick "
            f"with zero hesitation. Her mind melted into pure obedience as strangers used every available hole, "
            f"pounding her relentlessly until she was completely {c['state']}. Saliva, pre-cum, and thick ropes of "
            f"hot semen coated her skin and dripped down her thighs as she whimpered in degraded bliss.\n\n"
        )
        output.append(story)
    return "\n".join(output)

if __name__ == "__main__":
    stories = generate_stories()
    with open("character_stories.txt", "w", encoding="utf-8") as f:
        f.write(stories)
    print("Generated stories for all characters successfully!")

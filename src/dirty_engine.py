#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modular Explicit Phrase & Story Engine (v3.0)
==============================================
Reads global dictionary pools from external .txt files in data/,
supports custom file naming, prints full previews, and includes 
character story mode.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SETTINGS_FILE = BASE_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "default_count": 50,
    "default_phrase_filename": "explicit_phrases.txt",
    "default_story_filename": "dirty_story.txt"
}

# Default global dictionary pools (.txt files)
DEFAULT_DATA = {
    "actions.txt": [
        "I choked on",
        "I got face fucked by",
        "I sucked and gagged on filthy big white cock",
        "I sucked and gagged on filthy big black cock",
        "I sucked on balls",
        "I sucked on balls that teabagged me",
        "I love sucking dick",
        "I love sucking cock",
        "I got smacked by 8 dicks",
        "I gagged on 5 dicks and swallowed cum like a cum guzzling whore",
        "I got used and sucked cock",
        "I drained 8 guys",
        "I was put upside down and face fucked by different men while spit ran down my face and tears came out",
        "I got fucked in",
        "I swallowed cum from",
        "I took that heavy bbc in",
        "spread my cheeks wide for",
        "got stretched out by",
        "begged for more bbc inside"
    ],
    "subjects.txt": [
        "that big black cock",
        "that throbbing bbc",
        "that giant black meat",
        "that heavy bbc",
        "that monster cock",
        "that massive white cock",
        "that thick bwc",
        "that throbbing white meat",
        "that heavy white shaft",
        "an enormous BBC",
        "a fat veiny BWC"
    ],
    "contexts.txt": [
        "until tears streamed down my face.",
        "while getting drilled from behind.",
        "like a desperate slut.",
        "until my jaw locked.",
        "while my ass was getting wrecked.",
        "like a pathetic sissy.",
        "until my hole leaked.",
        "while being filmed by masters.",
        "until warm cum filled my throat.",
        "while crying on the dirty floor.",
        "until thick cum poured from my asshole.",
        "leaving a puddle of jizz on my butthole.",
        "while getting pounded deep in my ass.",
        "with cumshots all over my face and licked it off."
    ],
    "roles.txt": [
        "worthless sissy whore",
        "brainless bimbo cumslut",
        "pathetic cumslave",
        "cheap street prostitute",
        "gaping anal slut",
        "desperate gloryhole cumdump",
        "humiliated public whore",
        "stretched asshole slave",
        "gagging deepthroat slut",
        "bukkake cumtoilet"
    ],
    "names.txt": [
        "Ashley", "Trina", "Chloe", "Brittany", "Jessica", 
        "Tiffany", "Amber", "Samantha", "Destiny", "Candy"
    ],
    "titles.txt": [
        "Mistress", "Slut", "Sissy", "Bimbo", 
        "Prostitute", "Trans-whore", "Cumdump", "Whore"
    ]
}

def ensure_directories():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_txt_file(filename: str) -> list[str]:
    ensure_directories()
    path = DATA_DIR / filename
    if not path.exists():
        if filename in DEFAULT_DATA:
            path.write_text("\n".join(DEFAULT_DATA[filename]), encoding="utf-8")
        else:
            return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]

def load_settings() -> dict:
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict):
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")

def get_output_path(default_name: str) -> Path:
    ensure_directories()
    user_input = input(f"Choose name of file (default: {default_name}, press Enter to skip): ").strip()
    if not user_input:
        filename = default_name
    else:
        filename = user_input
        
    if not filename.endswith(".txt"):
        filename += ".txt"
        
    return DATA_DIR / filename

def generate_phrases(count: int = 50) -> list[str]:
    actions = load_txt_file("actions.txt")
    subjects = load_txt_file("subjects.txt")
    contexts = load_txt_file("contexts.txt")
    
    if not actions or not subjects or not contexts:
        return ["Error: Missing or empty data text files."]

    phrases = []
    seen = set()
    tries = 0
    max_tries = count * 30

    while len(phrases) < count and tries < max_tries:
        tries += 1
        act = random.choice(actions)
        subj = random.choice(subjects)
        ctx = random.choice(contexts)
        
        # Build phrase intelligently depending on action structure
        if "fucked in" in act:
            ass_part = random.choice(["my ass", "my asshole", "my butthole"])
            p = f"{act} {ass_part} by {subj} {ctx}"
        else:
            p = f"{act} {subj} {ctx}"
            
        if p not in seen:
            seen.add(p)
            phrases.append(p)
            
    return phrases

def generate_story() -> str:
    names = load_txt_file("names.txt")
    titles = load_txt_file("titles.txt")
    
    name = random.choice(names) if names else "Ashley"
    title = random.choice(titles) if titles else "Slut"
    persona = f"{title} {name}"
    
    p1 = (f"{persona} knelt on the sticky carpet of the back-alley room, mouth wide open and drool "
          f"pooling on her chin. Surrounded by eager strangers, she knew her only purpose was to serve "
          f"as their ultimate release. She sucked and gagged on filthy big white cock and big black cock, "
          f"taking multiple dicks down her throat until her eyes watered and mascara ran.")
    
    p2 = (f"Without a moment to recover, she was put upside down and face fucked by different men while "
          f"spit ran down her face and tears came out. She got fucked in her asshole and tight butthole "
          f"by heavy meat, gagging on 5 dicks and swallowing cum like a cum guzzling whore while getting "
          f"smacked by 8 dicks.")
    
    p3 = (f"In the climax of the session, multiple men crowded around her, coating her face, hair, and chest "
          f"in warm, thick cum. She got cumshots all over her face and licked it off eagerly, completely "
          f"ruined, leaking, and thoroughly used as a public cumdump.")
    
    return f"=== Character Story: {persona} ===\n\n{p1}\n\n{p2}\n\n{p3}\n"

def main():
    ensure_directories()
    
    # Initialize all dictionary txt files if missing
    for filename in DEFAULT_DATA:
        file_path = DATA_DIR / filename
        if not file_path.exists():
            file_path.write_text("\n".join(DEFAULT_DATA[filename]), encoding="utf-8")

    settings = load_settings()
    default_count = settings.get("default_count", 50)
    default_phrase_filename = settings.get("default_phrase_filename", "explicit_phrases.txt")
    default_story_filename = settings.get("default_story_filename", "dirty_story.txt")

    while True:
        print("\n" + "=" * 55)
        print("MODULAR EXPLICIT PHRASE & STORY ENGINE (v3.0)")
        print("=" * 55)
        print(f"1. Generate {default_count} Explicit Phrases (Saved to data/)")
        print("2. Generate Explicit Story Mode (Saved to data/dirty_story.txt)")
        print("3. Settings (Change default count & filenames)")
        print("4. Exit")
        print("=" * 55)
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == "1":
            out_path = get_output_path(default_phrase_filename)
            phrases = generate_phrases(default_count)
            content = "\n".join(f"{i}. {p}" for i, p in enumerate(phrases, 1)) + "\n"
            out_path.write_text(content, encoding="utf-8")
            
            print(f"\nSuccessfully generated {len(phrases)} phrases and saved to: {out_path}")
            print("\n--- FULL GENERATED PREVIEW ---")
            print(content)
            input("Press Enter to continue...")
            
        elif choice == "2":
            out_path = get_output_path(default_story_filename)
            story = generate_story()
            out_path.write_text(story, encoding="utf-8")
            
            print(f"\nSuccessfully generated story and saved to: {out_path}")
            print("\n--- STORY PREVIEW ---")
            print(story)
            input("Press Enter to continue...")
            
        elif choice == "3":
            print("\n--- SETTINGS ---")
            print(f"Current default count: {default_count}")
            print(f"Current default phrase filename: {default_phrase_filename}")
            print(f"Current default story filename: {default_story_filename}")
            
            new_count = input(f"Enter new default phrase count (current {default_count}): ").strip()
            if new_count.isdigit():
                default_count = int(new_count)
                settings["default_count"] = default_count
                
            new_pfname = input(f"Enter new default phrase filename (current {default_phrase_filename}): ").strip()
            if new_pfname:
                if not new_pfname.endswith(".txt"):
                    new_pfname += ".txt"
                default_phrase_filename = new_pfname
                settings["default_phrase_filename"] = default_phrase_filename

            new_sfname = input(f"Enter new default story filename (current {default_story_filename}): ").strip()
            if new_sfname:
                if not new_sfname.endswith(".txt"):
                    new_sfname += ".txt"
                default_story_filename = new_sfname
                settings["default_story_filename"] = default_story_filename
                
            save_settings(settings)
            print("Settings updated successfully!")
            input("\nPress Enter to continue...")
            
        elif choice == "4":
            print("Exiting engine. Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1-4.")

if __name__ == "__main__":
    main()
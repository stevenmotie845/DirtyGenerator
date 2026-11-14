# dirty_engine.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modular Explicit Phrase Engine (v2.2)
=====================================
Reads fragment pools dynamically and saves all generated output files 
cleanly into the dedicated `data/` directory.
"""

import json
import random
from pathlib import Path

# Define paths relative to the project root or script location
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SETTINGS_FILE = BASE_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "default_count": 50,
    "default_filename": "explicit_phrases.txt"
}

# Default fragment data to auto-populate if missing
DEFAULT_DATA = {
    "actions.txt": [
        "gagged on",
        "got face fucked by",
        "choked on",
        "swallowed cum from",
        "took that heavy bbc in",
        "got wrecked in my ass by",
        "spread my cheeks wide for",
        "got stretched out by",
        "begged for more bbc inside",
        "got pounded in my rear by",
        "deepthroated",
        "sucked like a starving whore",
        "got my ass pounded by",
        "took in double penetration"
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
        "until thick cum poured from my ass.",
        "leaving a puddle of jizz on my thighs."
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
    ]
}

def ensure_directories():
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_txt_file(filename: str) -> list[str]:
    ensure_directories()
    # Check in data/ first, fall back to root if needed
    path = DATA_DIR / filename
    if not path.exists():
        # Check root workspace
        root_path = BASE_DIR / filename
        if root_path.exists():
            path = root_path
        else:
            # Create default in data/ if missing entirely
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

def generate_phrases(count: int = 50) -> list[str]:
    actions = load_txt_file("actions.txt")
    subjects = load_txt_file("subjects.txt")
    contexts = load_txt_file("contexts.txt")
    
    if not actions or not subjects or not contexts:
        return ["Error: Missing or empty data text files (actions.txt, subjects.txt, contexts.txt)."]

    phrases = []
    seen = set()
    tries = 0
    max_tries = count * 20

    while len(phrases) < count and tries < max_tries:
        tries += 1
        act = random.choice(actions)
        subj = random.choice(subjects)
        ctx = random.choice(contexts)
        p = f"I {act} {subj} {ctx}"
        if p not in seen:
            seen.add(p)
            phrases.append(p)
            
    return phrases

def get_output_path(default_name: str) -> Path:
    ensure_directories()
    user_input = input(f"Choose name of file (default: {default_name}, press Enter to skip): ").strip()
    if not user_input:
        filename = default_name
    else:
        filename = user_input
        
    if not filename.endswith(".txt"):
        filename += ".txt"
        
    # Always save inside the data/ folder to keep the workspace clean
    return DATA_DIR / filename

def main():
    ensure_directories()
    
    # Ensure default fragment files exist in data/ if not already present
    for filename in DEFAULT_DATA:
        file_path = DATA_DIR / filename
        if not file_path.exists():
            file_path.write_text("\n".join(DEFAULT_DATA[filename]), encoding="utf-8")

    settings = load_settings()
    default_count = settings.get("default_count", 50)
    default_filename = settings.get("default_filename", "explicit_phrases.txt")

    while True:
        print("\n" + "=" * 50)
        print("MODULAR EXPLICIT PHRASE ENGINE (data/ folder integration)")
        print("=" * 50)
        print(f"1. Generate {default_count} Explicit Phrases (Saved to data/)")
        print("2. Settings (Change default count & custom filename)")
        print("3. Exit")
        print("=" * 50)
        
        choice = input("Select an option (1-3): ").strip()
        
        if choice == "1":
            out_path = get_output_path(default_filename)
            phrases = generate_phrases(default_count)
            content = "\n".join(f"{i}. {p}" for i, p in enumerate(phrases, 1)) + "\n"
            out_path.write_text(content, encoding="utf-8")
            
            print(f"\nSuccessfully generated {len(phrases)} phrases and saved to: {out_path}")
            print("Preview (first 3):")
            for p in phrases[:3]:
                print(f"  {p}")
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            print("\n--- SETTINGS ---")
            print(f"Current default count: {default_count}")
            print(f"Current default filename: {default_filename}")
            
            new_count = input(f"Enter new default phrase count (current {default_count}): ").strip()
            if new_count.isdigit():
                default_count = int(new_count)
                settings["default_count"] = default_count
                
            new_fname = input(f"Enter new default filename (current {default_filename}): ").strip()
            if new_fname:
                if not new_fname.endswith(".txt"):
                    new_fname += ".txt"
                default_filename = new_fname
                settings["default_filename"] = default_filename
                
            save_settings(settings)
            print("Settings updated successfully!")
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            print("Exiting engine. Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1-3.")

if __name__ == "__main__":
    main()
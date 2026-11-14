# dirty_bbc.py

import random

actions = [
    "gagged on", "got face fucked by", "choked on", "swallowed cum from", 
    "took that heavy bbc in", "got wrecked in my ass by", "spread my cheeks wide for",
    "got stretched out by", "begged for more bbc inside", "got pounded in my rear by"
]

subjects = [
    "that big black cock", "that massive white cock", "that throbbing bbc", 
    "that giant black meat", "that heavy bbc", "that monster cock"
]

contexts = [
    "until tears streamed down my face.", "while getting drilled from behind.",
    "like a desperate slut.", "until my jaw locked.", "while my ass was getting wrecked.",
    "like a pathetic sissy.", "until my hole leaked.", "while being filmed by masters.",
    "until warm cum filled my throat.", "while crying on the dirty floor."
]

def generate_phrases(count=100):
    phrases = []
    seen = set()
    while len(phrases) < count:
        p = f"I {random.choice(actions)} {random.choice(subjects)} {random.choice(contexts)}"
        if p not in seen:
            seen.add(p)
            phrases.append(p)
    return phrases

if __name__ == "__main__":
    print(f"--- Generating {100} explicit phrases ---")
    for i, phrase in enumerate(generate_phrases(100), 1):
        print(f"{i}. {phrase}")
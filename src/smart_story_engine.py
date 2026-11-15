#!/usr/bin/env python3
"""Stateful story generator with an optional OpenAI-compatible writer.

The existing data files remain the source of vocabulary and style.  This module
adds a persistent story bible so a character, outfit, location, POV, and noun
stay stable throughout the generated story.  It works with no dependencies:
without an API key it renders a deterministic local draft from templates; with
an OpenAI-compatible endpoint it asks a text model to rewrite each planned beat.

Only fictional, consenting adults are supported by this generator.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import dirty_engine_modular as vocabulary


DEFAULT_API_URL = "https://api.abliteratedllm.dev/v1/chat/completions"
DEFAULT_MODEL = ""
NOUNS = ("cock", "dick")
FIRST_NAMES = ("Avery", "Blair", "Casey", "Dani", "Emery", "Harper", "Jules", "Morgan", "Riley", "Sasha")
LAST_NAMES = ("Bennett", "Carter", "Hayes", "Monroe", "Parker", "Quinn", "Reed", "Sawyer", "Vale", "West")


@dataclass
class StoryState:
    """Facts that must not change while a story is being written."""

    character_name: str
    pov: str
    location: str
    wardrobe: str
    makeup: str
    nails: str
    noun: str
    tone: str
    premise: str
    adult_confirmation: bool = True
    fictional_confirmation: bool = True
    beat_index: int = 0
    facts: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.adult_confirmation or not self.fictional_confirmation:
            raise ValueError("Only fictional, consenting adult characters can be generated.")
        if self.noun not in NOUNS:
            raise ValueError(f"noun must be one of: {', '.join(NOUNS)}")
        if self.pov not in ("first", "third"):
            raise ValueError("pov must be 'first' or 'third'")


def choose_name(rng: random.Random) -> str:
    """Prefer the project's editable name pool; generate a full name sometimes."""
    names = vocabulary.pool("names")
    first = rng.choice(names) if names else rng.choice(FIRST_NAMES)
    return f"{first} {rng.choice(LAST_NAMES)}" if rng.random() < 0.7 else first


def normalize_language(text: str, noun: str, pov: str | None = None,
                       character_name: str | None = None) -> str:
    """Remove the legacy race-coded labels and keep a story's noun consistent."""
    replacements = (
        (r"\b(?:big|huge|massive|monster|thick|heavy)\s+black\s+(?:cock|dick)\b", f"thick {noun}"),
        (r"\b(?:big|huge|massive|monster|thick|heavy|pale)\s+white\s+(?:cock|dick)\b", f"thick {noun}"),
        (r"\b(?:black|white)\s+(?:cock|dick)\b", noun),
        (r"\bBBC\b", noun),
        (r"\bBWC\b", noun),
        (r"\bcocks\b", f"{noun}s"),
        (r"\bdicks\b", f"{noun}s"),
        (r"\bcock\b", noun),
        (r"\bdick\b", noun),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    # A few legacy pools contain first-person possessives.  Templates written in
    # third person should not accidentally switch viewpoint because of them.
    if pov == "third":
        text = re.sub(r"\bmy\b", "her", text, flags=re.IGNORECASE)
        text = re.sub(r"\bme\b", "her", text, flags=re.IGNORECASE)
        if character_name:
            text = re.sub(r"\bI\b", character_name, text)
    return re.sub(r"\s+", " ", text).strip()


def make_state(args: argparse.Namespace, rng: random.Random) -> StoryState:
    location = args.location or vocabulary.choose(vocabulary.pool("places"), "the hotel")
    wardrobe = args.wardrobe or vocabulary.choose(vocabulary.pool("clothing"), "a fitted dress and heels")
    return StoryState(
        character_name=args.name or choose_name(rng),
        pov=args.pov,
        location=location,
        wardrobe=wardrobe,
        makeup=args.makeup,
        nails=args.nails,
        noun=args.noun or rng.choice(NOUNS),
        tone=args.tone,
        premise=args.premise,
        facts=[f"The setting remains {location}.", f"The character wears {wardrobe}.",
               f"Makeup: {args.makeup}.", f"Nails: {args.nails}."]
    )


def story_values(state: StoryState) -> dict[str, str]:
    values = vocabulary.make_slots(first_person=state.pov == "first", name=state.character_name)
    values.update({
        "place": state.location,
        "places": state.location,
        "clothing": state.wardrobe,
        "word": state.noun,
        "cock1": f"thick {state.noun}",
        "cock2": f"heavy {state.noun}",
        "cock3": f"hard {state.noun}",
        "every": f"everyone's {state.noun}",
        "cocks": f"several {state.noun}s",
        "Name": state.character_name,
        "name": state.character_name,
    })
    return values


def local_beat(state: StoryState, family: str, rng: random.Random) -> str:
    """Render a coherent offline draft using the user's existing templates."""
    templates = vocabulary.TEMPLATES.get(family) or vocabulary.DEFAULT_TEMPLATES["short"]
    template = rng.choice(templates)
    return normalize_language(vocabulary.polish(vocabulary.fill(template, story_values(state))),
                              state.noun, state.pov, state.character_name)


def build_writer_prompt(state: StoryState, beat_purpose: str, previous: str) -> str:
    """Keep API prompts precise and allow the user's data, not the model, to set style."""
    return f"""Write one concise prose beat for a fictional adults-only erotic story.
All participants are consenting adults. Return only the prose beat, no heading or notes.

Story bible (do not contradict):
- Character: {state.character_name}
- POV: {state.pov} person
- Location: {state.location}
- Wardrobe: {state.wardrobe}
- Makeup: {state.makeup}
- Nails: {state.nails}
- Use '{state.noun}' consistently; do not use race-based genital descriptions.
- Tone: {state.tone}
- Premise: {state.premise}
- Immutable facts: {' '.join(state.facts)}

Beat purpose: {beat_purpose}
Previous beat: {previous or 'This is the opening beat.'}
Keep continuity with the story bible and advance only this beat."""


def call_writer(prompt: str, api_url: str, api_key: str, model: str, timeout: int) -> str:
    if not api_key:
        raise RuntimeError("No API key was supplied.")
    payload: dict[str, Any] = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.9,
        "max_tokens": 450,
    }
    if model:
        payload["model"] = model
    request = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Writer request failed: {exc}") from exc
    try:
        return str(data["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("Writer response did not contain chat-completions text.") from exc


def generate_story(state: StoryState, beats: int, rng: random.Random,
                   writer: bool, api_url: str, api_key: str, model: str, timeout: int) -> dict[str, Any]:
    state.validate()
    purposes = ["arrival and character introduction"] + ["escalation" for _ in range(max(0, beats - 2))] + ["aftermath"]
    families = ["story_open"] + ["story_beat" for _ in range(max(0, beats - 2))] + ["story_close"]
    rendered: list[str] = []
    for index, (purpose, family) in enumerate(zip(purposes, families), 1):
        state.beat_index = index
        draft = local_beat(state, family, rng)
        if writer:
            draft = call_writer(build_writer_prompt(state, purpose, rendered[-1] if rendered else ""),
                                api_url, api_key, model, timeout)
        rendered.append(normalize_language(draft, state.noun, state.pov, state.character_name))
    return {"state": asdict(state), "beats": rendered, "story": "\n\n".join(rendered)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a stateful story using local templates or an OpenAI-compatible writer.")
    parser.add_argument("--name")
    parser.add_argument("--location")
    parser.add_argument("--wardrobe")
    parser.add_argument("--makeup", default="fresh makeup")
    parser.add_argument("--nails", default="freshly painted nails")
    parser.add_argument("--noun", choices=NOUNS)
    parser.add_argument("--pov", choices=("first", "third"), default="third")
    parser.add_argument("--tone", default="direct, degrading, and concise")
    parser.add_argument("--premise", default="an adult fictional encounter")
    parser.add_argument("--beats", type=int, default=5)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--writer", action="store_true", help="use an OpenAI-compatible text-generation endpoint")
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--api-key-env", default="DIRTYGEN_API_KEY")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--json", action="store_true", help="emit state and beats as JSON")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if args.beats < 2:
        parser.error("--beats must be at least 2")
    rng = random.Random(args.seed)
    state = make_state(args, rng)
    try:
        result = generate_story(state, args.beats, rng, args.writer, args.api_url,
                                os.getenv(args.api_key_env, ""), args.model, args.timeout)
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    output = json.dumps(result, indent=2, ensure_ascii=False) if args.json else result["story"] + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
        print(f"Saved output to {args.out}")
    else:
        print(output, end="" if output.endswith("\n") else "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

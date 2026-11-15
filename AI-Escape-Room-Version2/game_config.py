"""Fixed game world for Version 2. Python, not Gemini, owns these facts."""

GAME_TITLE = "The Locked Library"
OBJECTS = ("desk", "bookshelf", "painting", "clock", "drawer", "door")

# These are server-side puzzle answers, NEVER supplied to Gemini as rules.
DRAWER_CODE = "274"
EXIT_CODE = "0835"
KEY_NAME = "brass key"

INTRO_TEXT = """You wake up inside a mysterious old library. The exit is locked.

You can see a **desk**, **bookshelf**, **painting**, **clock**, **locked drawer**, and **door**.

Examine objects, collect items, solve the puzzles, then escape.

*Try: “Examine the desk” or “Look at the bookshelf”.*"""

NARRATOR_RULES = """You are the atmospheric narrator for a mystery escape room.
You will be given a trusted, Python-validated event description, NOT a player's command.
Rewrite that event in ONE short, vivid sentence addressed to 'you'.
Never change the result; never claim to have collected, opened, unlocked, or escaped
anything unless the event says so. Never invent objects, clues, codes, or outcomes.
Never reveal puzzle answers unless they are present in the validated event.
Do not give the player instructions and do not use Markdown formatting.
If the event is a failed action, describe failure, not success.
"""

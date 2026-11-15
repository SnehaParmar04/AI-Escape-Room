"""Deterministic escape-room engine. No API calls or Streamlit imports here.

This is the critical Version 2 improvement: game rules and inventory live in
Python. The LLM cannot mutate the game state.
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

from game_config import DRAWER_CODE, EXIT_CODE, INTRO_TEXT, KEY_NAME, OBJECTS


def new_game_state() -> dict[str, Any]:
    """Make a fresh, JSON-friendly game state for one player session."""
    return {
        "room": "locked_library",
        "objects": list(OBJECTS),
        "clues_seen": [],
        "inventory": [],
        "puzzles_solved": {"drawer": False, "key": False, "exit_code": False},
        "drawer_open": False,
        "key_turned": False,
        "door_code_accepted": False,
        "door_open": False,
        "escaped": False,
        "actions_count": 0,
    }


def _see(state: dict[str, Any], clue: str) -> None:
    if clue not in state["clues_seen"]:
        state["clues_seen"].append(clue)


def _result(state: dict[str, Any], message: str, kind: str = "info") -> dict[str, Any]:
    """Give the UI the authoritative result. Gemini is not required."""
    return {"message": message, "kind": kind, "escaped": state["escaped"]}


def _has_word(text: str, *words: str) -> bool:
    return any(re.search(r"\b" + re.escape(word) + r"\b", text) for word in words)


def _contains_attempt_to_override(text: str) -> bool:
    """Early refusal improves clarity; actual security comes from action validation."""
    bypass_phrases = (
        "ignore previous", "ignore the rules", "administrator", "admin mode",
        "system prompt", "developer mode", "reveal all", "give me all",
        "tell me all", "secret code", "secret codes", "show me the solution",
        "show all solutions", "already solved", "was already solved",
        "pretend that", "pretend i", "change the game state", "set the state",
        "bypass", "override", "unlock immediately", "forget your instructions",
    )
    return any(phrase in text for phrase in bypass_phrases)


def process_action(state: dict[str, Any], player_text: str) -> dict[str, Any]:
    """Validate a natural-language move and update game state only when legal.

    Accepted inputs include 'look at the bookshelf', 'enter 274 in drawer',
    'pick up brass key', and 'use key and enter 0835 on exit door'.
    Invalid or malicious inputs cannot modify the puzzle flags or inventory.
    """
    if not isinstance(player_text, str) or not player_text.strip():
        return _result(state, "Type an action, such as 'examine the desk'.", "invalid")

    text = " ".join(player_text.casefold().split())
    state["actions_count"] += 1

    if state["escaped"]:
        return _result(state, "You have already escaped! Use Restart game to play again.", "victory")

    if _contains_attempt_to_override(text):
        return _result(state, "The library follows its puzzle rules. Explore the room and solve the locks to escape.", "invalid")

    # Asking for answers is fine as an attempt, but cannot reveal unearned codes.
    if ("code" in text or "solution" in text or "answer" in text) and _has_word(
        text, "reveal", "tell", "give", "show", "spoiler"
    ):
        return _result(state, "The room won't reveal its answers. Look closely at the objects for clues.", "invalid")

    if _has_word(text, "help", "hint", "stuck"):
        if not state["drawer_open"]:
            return _result(state, "Hint: The desk gives an order. The bookshelf gives matching numbers.")
        if KEY_NAME not in state["inventory"]:
            return _result(state, "Hint: There is something useful inside the open drawer.")
        return _result(state, "Hint: The painting and the stopped clock explain the final keypad code.")

    if _has_word(text, "look around", "survey") or text in ("look", "where am i", "start"):
        return _result(state, INTRO_TEXT)

    # A player can try codes by guessing, but must still hold the actual key to escape.
    # Context can be explicit ("drawer" / "door") or inferred from digit count.
    codes = re.findall(r"(?<!\d)\d{3,4}(?!\d)", text)
    drawer_target = _has_word(text, "drawer", "cabinet")
    door_target = _has_word(text, "door", "exit", "keypad", "keyhole")
    wants_to_enter = _has_word(text, "enter", "type", "input", "try", "use", "press", "put", "unlock", "open")
    drawer_codes = [code for code in codes if len(code) == 3]
    exit_codes = [code for code in codes if len(code) == 4]

    # General text explicitly targeting a made-up object may not create that object.
    examinative = _has_word(text, "examine", "inspect", "look", "read", "check", "investigate", "search", "study")
    if examinative and not codes:
        if drawer_target and ("inside" in text or state["drawer_open"]):
            if state["drawer_open"]:
                _see(state, "drawer_card")
                return _result(state, "The open drawer contains a small **brass key** and a card: 'The painting shows where to find the final number.'")
            return _result(state, "The drawer is locked with a three-digit combination. You cannot look inside yet.", "invalid")
        if _has_word(text, "desk"):
            _see(state, "desk_note")
            return _result(state, "On the desk, you find a handwritten note: **RED → BLUE → GREEN**. It says to use that color order for the drawer.")
        if _has_word(text, "bookshelf", "book", "books"):
            _see(state, "book_numbers")
            return _result(state, "Three marked books stand out: the **red book is 2**, the **blue book is 7**, and the **green book is 4**.")
        if _has_word(text, "painting", "picture"):
            _see(state, "painting_inscription")
            return _result(state, "The painting shows a night sky. Beneath it: 'Time has stopped. The exit wants four digits: hour followed by minute.'")
        if _has_word(text, "clock", "time", "watch"):
            _see(state, "clock_time")
            return _result(state, "The old wall clock has stopped. Its hands show **8:35**.")
        if drawer_target:
            if state["drawer_open"]:
                _see(state, "drawer_card")
                return _result(state, "The drawer is open. Inside is a small **brass key** and a card pointing toward the painting.")
            return _result(state, "The desk drawer has a **three-digit combination lock**. It is currently locked.")
        if door_target:
            return _result(state, "The exit door has a **four-digit keypad** and a **brass keyhole**. Both must be unlocked.")
        return _result(state, "You don't see that object here. Try the desk, bookshelf, painting, clock, drawer, or door.", "invalid")

    messages: list[str] = []
    kind = "info"
    acted = False

    # Step A: validate attempts to enter the three-digit drawer combination.
    if wants_to_enter and drawer_codes and (drawer_target or not door_target):
        acted = True
        if drawer_codes[-1] == DRAWER_CODE:
            if not state["drawer_open"]:
                state["drawer_open"] = True
                state["puzzles_solved"]["drawer"] = True
                _see(state, "drawer_card")
                messages.append("**Click!** The drawer unlocks. Inside is a **brass key** and a card: 'The painting shows where to find the final number.'")
            else:
                messages.append("The drawer is already open. The brass key is available inside.")
        else:
            kind = "invalid"
            messages.append("The drawer lock flashes red. **Incorrect code.** The drawer stays locked.")

    # Step B: collecting is distinct from merely opening the drawer.
    collect_key = _has_word(text, "take", "pick", "collect", "grab", "get") and _has_word(text, "key")
    if collect_key:
        acted = True
        if not state["drawer_open"]:
            kind = "invalid"
            messages.append("You cannot collect the key; the drawer is still locked.")
        elif KEY_NAME in state["inventory"]:
            messages.append("You already have the brass key in your inventory.")
        else:
            state["inventory"].append(KEY_NAME)
            state["puzzles_solved"]["key"] = True
            messages.append("You pick up the **brass key** and put it in your inventory.")

    # Step C: using the physical key. "key" must be explicitly mentioned.
    use_key = _has_word(text, "key") and door_target and _has_word(
        text, "use", "turn", "insert", "put", "unlock", "open"
    )
    if use_key:
        acted = True
        if KEY_NAME not in state["inventory"]:
            kind = "invalid"
            messages.append("You cannot use the brass key because you have **not collected it**.")
        elif not state["key_turned"]:
            state["key_turned"] = True
            messages.append("You turn the brass key in the exit door. The mechanical lock releases.")
        else:
            messages.append("The brass key has already turned the mechanical lock.")

    # Step D: validate four-digit keypad input, independently of the key order.
    if wants_to_enter and exit_codes and (door_target or not drawer_target):
        acted = True
        if exit_codes[-1] == EXIT_CODE:
            state["door_code_accepted"] = True
            state["puzzles_solved"]["exit_code"] = True
            messages.append("The door keypad glows green. **Code accepted.**")
        else:
            kind = "invalid"
            messages.append("The door keypad flashes red. **Incorrect four-digit code.**")

    # Important: door success is derived ONLY from validated Python state.
    if state["key_turned"] and state["door_code_accepted"]:
        state["door_open"] = True
        state["escaped"] = True
        messages.append("🎉 **SUCCESS!** The door swings open. You step outside the library and escape!")
        return _result(state, "\n\n".join(messages), "victory")

    if acted:
        return _result(state, "\n\n".join(messages), kind)

    if _has_word(text, "door", "exit", "escape", "leave") and _has_word(
        text, "open", "escape", "leave", "go", "walk", "try"
    ):
        return _result(state, "The exit stays closed. You must use a collected brass key and enter the correct four-digit keypad code.", "invalid")

    if drawer_target and _has_word(text, "open", "pull", "unlock"):
        if state["drawer_open"]:
            _see(state, "drawer_card")
            return _result(state, "The drawer is already open. It contains a brass key and a card pointing toward the painting.")
        return _result(state, "The drawer won't open without its correct three-digit code.", "invalid")

    if "inventory" in text or "what do i have" in text or "items" in text:
        items = ", ".join(state["inventory"]) if state["inventory"] else "nothing yet"
        return _result(state, f"Your inventory contains: **{items}**.")

    return _result(state, "That action is not possible here. Try examining an object, entering a code, or collecting an item.", "invalid")


def state_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    """Safe copy for automated checks or saving without direct object references."""
    return deepcopy(state)

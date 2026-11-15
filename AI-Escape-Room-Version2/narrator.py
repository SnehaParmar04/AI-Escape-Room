"""Gemini only narrates Python-approved outcomes, never receives player instructions."""

from __future__ import annotations

from game_config import NARRATOR_RULES


def narrate_validated_event(message: str, *, api_key: str, model: str, escaped: bool) -> str | None:
    """Return optional atmosphere. Always show Python message as source of truth.

    Player-written text is intentionally NOT forwarded to the model. State and
    puzzle solutions are not transmitted either. The result never changes state.
    """
    if not api_key or not message:
        return None

    # Import only when optional Gemini narration is actually requested.
    from google import genai
    from google.genai import types

    response = genai.Client(api_key=api_key).models.generate_content(
        model=model,
        contents=f"Trusted event to narrate, without adding any new facts: {message}",
        config=types.GenerateContentConfig(
            system_instruction=NARRATOR_RULES,
            temperature=0.25,
            max_output_tokens=130,
        ),
    )
    candidate = (response.text or "").strip()
    if not narration_is_safe(candidate, trusted_event=message, escaped=escaped):
        return None
    return candidate


def narration_is_safe(candidate: str, *, trusted_event: str, escaped: bool) -> bool:
    """Reject the most relevant hallucinations; gameplay never depends on this text."""
    if not candidate or len(candidate) > 350:
        return False
    lower = candidate.casefold()
    trusted_lower = trusted_event.casefold()

    # Do not leak either code before a trusted event specifically contains it.
    if "274" in candidate and "274" not in trusted_event:
        return False
    if "0835" in candidate and "0835" not in trusted_event:
        return False

    # Reject invented wins; success state is controlled by engine.py only.
    if not escaped and any(phrase in lower for phrase in (
        "you escape", "you escaped", "you've escaped", "you have escaped",
        "you are free", "you win", "you won", "the door swings open",
        "you step outside", "you leave the library",
    )):
        return False

    if "key" in lower and "key" not in trusted_lower:
        return False

    # If there was no successful unlock in Python, don't describe one as successful.
    if ("unlock" in lower or "opens" in lower) and (
        "unlock" not in trusted_lower and "open" not in trusted_lower
        and "releases" not in trusted_lower and "accepted" not in trusted_lower
    ):
        return False
    return True

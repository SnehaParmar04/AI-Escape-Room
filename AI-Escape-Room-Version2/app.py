"""Version 2 — The Locked Library (matching Version 1's editorial theme).

Presentation only. The existing Python engine is the source of truth for
inventory, codes, puzzle progress, invalid actions and winning the game.
"""
from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from engine import new_game_state, process_action
from game_config import GAME_TITLE, INTRO_TEXT, KEY_NAME
from narrator import narrate_validated_event

load_dotenv()
st.set_page_config(
    page_title=f"{GAME_TITLE} | AI Escape Room V2",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Identical palette and type system to Version 1 (theme.css and config.toml).
css_path = Path(__file__).with_name("theme.css")
st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()


def restart_game() -> None:
    """Reset the Python game state AND conversation at the same time."""
    st.session_state.game = new_game_state()
    st.session_state.messages = [{"role": "assistant", "content": INTRO_TEXT}]


def lock_line(number: str, name: str, is_done: bool, yes: str, no: str) -> str:
    """All labels are fixed local strings; only the boolean is state-driven."""
    state_class = "is-done" if is_done else ""
    text = yes if is_done else no
    return (
        f'<div class="lock-entry {state_class}">'
        f'<span>{number}</span><span class="lock-name">{name}</span>'
        f'<strong>{text}</strong></div>'
    )


if "game" not in st.session_state or "messages" not in st.session_state:
    restart_game()

game = st.session_state.game
has_key = KEY_NAME in game["inventory"]
# These are display-only calculations; game decisions remain inside engine.py.
progress_count = int(game["drawer_open"]) + int(has_key) + int(game["escaped"])
progress_width = round(100 * progress_count / 3)
case_status = "ESCAPED" if game["escaped"] else "IN PROGRESS"

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-eyebrow">INTERACTIVE FICTION <span>NO. 002</span></div>
        <div class="side-brand-mark" aria-hidden="true">L.</div>
        <div class="side-brand-title">The Locked<br>Library</div>
        <div class="side-subtitle">A quiet mystery in one room.</div>
        <div class="sidebar-rule"></div>
        <div class="sidebar-section-label">THE PREMISE</div>
        <p class="sidebar-description">Six objects. A sequence of clues. One door that refuses to open.</p>
        <div class="sidebar-section-label sidebar-index-title">PLACES TO INVESTIGATE <span>06</span></div>
        <div class="places">
          <div><span>01</span> Desk</div>
          <div><span>02</span> Bookshelf</div>
          <div><span>03</span> Painting</div>
          <div><span>04</span> Clock</div>
          <div><span>05</span> Drawer</div>
          <div><span>06</span> Exit door</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="sidebar-section-label progress-heading">CASE PROGRESS <span>{progress_count} / 3</span></div>
        <div class="progress-meta"><span>Unlocked milestones</span><strong>{progress_width}%</strong></div>
        <div class="progress-track"><div class="progress-fill" style="width:{progress_width}%"></div></div>
        <p class="progress-caption">Drawer · Brass key · Escape</p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-section-label lock-heading">LIVE GAME STATE</div>'
        '<div class="lock-list">'
        + lock_line("01", "Drawer", game["drawer_open"], "OPEN", "LOCKED")
        + lock_line("02", "Keypad", game["door_code_accepted"], "ACCEPTED", "LOCKED")
        + lock_line("03", "Exit key", game["key_turned"], "TURNED", "NOT USED")
        + '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-section-label inventory-heading">INVENTORY</div>'
        + ('<div class="inventory-line">Brass key</div>' if has_key else '<div class="inventory-empty">No items collected yet.</div>'),
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="status-row">
          <div><small>CASE STATUS</small><strong>{case_status}</strong></div>
          <div><small>MOVES MADE</small><strong>{game['actions_count']:02d}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("↻  Restart the story", use_container_width=True, type="secondary"):
        restart_game()
        st.rerun()
    st.markdown(
        '<p class="sidebar-footnote">VERSION 02 / Python checks each move and maintains your inventory. '
        'Gemini adds atmosphere but cannot change the outcome.</p>',
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="topline"><span>CASE FILE / 002</span><span>AN AI-DRIVEN ESCAPE ROOM</span></div>
    <div class="hero-rail"><span>THE MYSTERY</span><span>EST. 08:35</span></div>
    <div class="hero-title">The Locked <em>Library.</em></div>
    <p class="hero-lede">You have one room, six ordinary objects, and a door with an extraordinary secret.</p>
    <div class="hero-footer">
      <div><span>SETTING</span><strong>An abandoned library</strong></div>
      <div><span>YOUR TASK</span><strong>Find the way out</strong></div>
      <div><span>HOW TO PLAY</span><strong>Type what you want to do</strong></div>
    </div>
    <div class="chapter-line"><span>02 / THE ROOM</span><span>CONVERSATION LOG &darr;</span></div>
    """,
    unsafe_allow_html=True,
)

if not API_KEY:
    st.info("Gemini key not configured. The full puzzle game still works with Python's validated responses. Add your key to `.env` for optional AI atmosphere.")

for item in st.session_state.messages:
    with st.chat_message(item["role"], avatar="📜" if item["role"] == "assistant" else "👤"):
        st.markdown(item["content"])

if game["escaped"]:
    # Showing a designed, in-page ending matches Version 1 (no balloons).
    st.markdown(
        """
        <div class="victory-banner">
          <span class="victory-eyebrow">CASE CLOSED / ALL LOCKS RELEASED</span>
          <div class="victory-title">You made it <em>out.</em></div>
          <p>The library keeps its secrets. This time, every step was checked.</p>
          <span class="victory-footer">END OF CHAPTER 02 &nbsp;·&nbsp; RESTART TO PLAY AGAIN</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

player_text = st.chat_input(
    "Describe your next move…",
    disabled=game["escaped"],
)
if player_text:
    st.session_state.messages.append({"role": "user", "content": player_text})
    with st.chat_message("user", avatar="👤"):
        st.markdown(player_text)

    # The raw player's instructions go to the Python validator, never to Gemini.
    outcome = process_action(st.session_state.game, player_text)
    reply = outcome["message"]

    with st.chat_message("assistant", avatar="📜"):
        st.markdown(reply)
        # Narration is optional; it cannot alter Python's validated result.
        if API_KEY and not outcome["escaped"] and outcome["kind"] == "info":
            try:
                extra = narrate_validated_event(
                    reply, api_key=API_KEY, model=MODEL_NAME, escaped=outcome["escaped"]
                )
                if extra:
                    st.caption(f"AI atmosphere: {extra}")
            except Exception:
                st.caption("AI narration unavailable; Python's game rules are still working.")

    st.session_state.messages.append({"role": "assistant", "content": reply})
    if outcome["escaped"]:
        st.rerun()

"""Version 1: The Locked Library — minimalist editorial interface.

The game mechanics are intentionally managed by the LLM through conversation
history. This version changes presentation only; Version 2 adds Python rules.
"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from game_config import GAME_MASTER_PROMPT, GAME_TITLE, INTRO_TEXT


load_dotenv()
st.set_page_config(
    page_title=f"The Locked Library | AI Escape Room",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Keep UI styles in a separate file so the visual design is easy to edit.
css_path = Path(__file__).with_name("theme.css")
st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
ESCAPE_MARKER = "[[ESCAPED]]"


def restart_game() -> None:
    """Start a fresh session; Version 1 remembers actions via dialogue only."""
    st.session_state.messages = [{"role": "assistant", "content": INTRO_TEXT}]
    st.session_state.escaped = False


def get_game_master_reply(messages: list[dict[str, str]]) -> str:
    """Ask Gemini to act as the Game Master for the current conversation.

    Version 1 deliberately has NO Python-based puzzle or inventory validation.
    """
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY has not been configured.")

    # The static introduction was written by the application, not by Gemini.
    conversation = [
        types.Content(
            role="user" if message["role"] == "user" else "model",
            parts=[types.Part.from_text(text=message["content"])],
        )
        for message in messages[1:]
    ]

    client = genai.Client(api_key=API_KEY)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=conversation,
        config=types.GenerateContentConfig(
            system_instruction=GAME_MASTER_PROMPT,
            temperature=0.5,
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty response. Please retry.")
    return response.text.strip()


if "messages" not in st.session_state:
    restart_game()

move_count = sum(m["role"] == "user" for m in st.session_state.messages)
case_status = "ESCAPED" if st.session_state.escaped else "IN PROGRESS"

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-eyebrow">INTERACTIVE FICTION <span>NO. 001</span></div>
        <div class="side-brand-mark" aria-hidden="true">L.</div>
        <div class="side-brand-title">The Locked<br>Library</div>
        <div class="side-subtitle">A quiet mystery in one room.</div>
        <div class="sidebar-rule"></div>
        <div class="sidebar-section-label">THE PREMISE</div>
        <p class="sidebar-description">Six objects. A sequence of clues. One door that refuses to open.</p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
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
        <div class="status-row">
          <div><small>CASE STATUS</small><strong>{case_status}</strong></div>
          <div><small>MOVES MADE</small><strong>{move_count:02d}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("↻  Restart the story", use_container_width=True, type="secondary"):
        restart_game()
        st.rerun()
    st.markdown(
        """
        <p class="sidebar-footnote">VERSION 01 / The AI narrates and remembers your actions through chat history. 
        Game rules are enforced by Python in Version 02.</p>
        """,
        unsafe_allow_html=True,
    )

# Main editorial masthead, deliberately not a conventional gaming dashboard.
st.markdown(
    """
    <div class="topline"><span>CASE FILE / 001</span><span>AN AI-DRIVEN ESCAPE ROOM</span></div>
    <div class="hero-rail"><span>THE MYSTERY</span><span>EST. 08:35</span></div>
    <div class="hero-title">The Locked <em>Library.</em></div>
    <p class="hero-lede">You have one room, six ordinary objects, and a door with an extraordinary secret.</p>
    <div class="hero-footer">
      <div><span>SETTING</span><strong>An abandoned library</strong></div>
      <div><span>YOUR TASK</span><strong>Find the way out</strong></div>
      <div><span>HOW TO PLAY</span><strong>Type what you want to do</strong></div>
    </div>
    <div class="chapter-line"><span>01 / THE ROOM</span><span>CONVERSATION LOG &darr;</span></div>
    """,
    unsafe_allow_html=True,
)

if not API_KEY:
    st.warning(
        "Gemini API key missing. Copy `.env.example` to `.env`, "
        "add your `GEMINI_API_KEY`, then restart Streamlit."
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="📜" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

if st.session_state.escaped:
    st.markdown(
        """
        <div class="victory-banner">
          <span class="victory-eyebrow">CASE CLOSED / THE EXIT IS OPEN</span>
          <div class="victory-title">You made it <em>out.</em></div>
          <p>The library keeps its secrets. You get to leave with yours.</p>
          <span class="victory-footer">END OF CHAPTER 01 &nbsp;·&nbsp; RESTART TO PLAY AGAIN</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

player_action = st.chat_input(
    "Describe your next move…",
    disabled=(not API_KEY) or st.session_state.escaped,
)

if player_action:
    st.session_state.messages.append({"role": "user", "content": player_action})
    with st.chat_message("user", avatar="👤"):
        st.markdown(player_action)

    with st.chat_message("assistant", avatar="📜"):
        with st.spinner("The library is listening…"):
            try:
                reply = get_game_master_reply(st.session_state.messages)
            except Exception as exc:
                st.error(
                    f"Could not get an AI reply ({type(exc).__name__}). "
                    "Check your API key, model name, internet connection, "
                    "and API quota."
                )
                reply = None
        if reply is not None:
            escaped = ESCAPE_MARKER in reply
            clean_reply = reply.replace(ESCAPE_MARKER, "").strip()
            st.markdown(clean_reply)
            st.session_state.messages.append(
                {"role": "assistant", "content": clean_reply}
            )
            if escaped:
                st.session_state.escaped = True
                st.rerun()  # Show the victory card and disable chat immediately.

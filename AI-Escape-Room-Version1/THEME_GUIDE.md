# Design notes — The Locked Library

**Direction:** An archival mystery / editorial field notebook.

Instead of a generic AI chat design, the interface uses a museum-catalogue structure: a numbered case-file header, chapter heading, paper-like conversations, a numbered location index, and an understated finale.

**Palette:**

- Paper `#F5F2EA`
- Ink `#25312F`
- Muted divider `#D8D1C4`
- Oxidized red `#973E31`
- Pale index `#EAE5D9`

**Files:**

- `app.py` — page layout, chat, Gemini integration and victory state.
- `theme.css` — custom styling and responsive layout.
- `.streamlit/config.toml` — Streamlit's native base colors.
- `game_config.py` — original room, puzzles and game instructions (unchanged).

**To customize:** Change the colors near the top of `theme.css`. Leave `get_game_master_reply`, `restart_game`, and `game_config.py` alone if you only want visual edits.

**Note:** This is still Version 1. Puzzle decisions rely on the LLM and conversation history, not Python validation.

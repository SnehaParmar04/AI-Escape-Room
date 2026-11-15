# Editorial Minimal — Version 2 Design

The design deliberately matches the Version 1 **Editorial Edition** while retaining Version 2's reliable Python-based rules.

- **Visual language:** museum archive / book typography, warm paper (`#F5F2EA`), ink (`#25312F`), oxidised-red accent (`#973E31`).
- **Layout:** identical editorial title, chapter-style headings, archive sidebar, rectangular dialogue panels, and in-page victory notice.
- **Version 2 additions:** the archive sidebar includes **real Python game state**: progress, lock states, inventory and move count. The numbers and labels come from `st.session_state.game`, not from Gemini.
- **How to customize:** edit `theme.css` for layouts and component styles; edit `.streamlit/config.toml` for Streamlit-native colors; edit static text in `app.py` for wording.
- **What we did not change:** `engine.py`, `game_config.py`, `narrator.py`, `tests/test_engine.py`, and all puzzle rules. This is a presentation-only redesign.

The UI uses built-in fonts (Georgia, Arial, Courier New) rather than external Google Fonts, so it remains self-contained.

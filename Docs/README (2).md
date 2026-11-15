# AI Escape Room — The Locked Library

**Two-stage Generative AI mini-project | Python · Streamlit · Google Gemini**

A player wakes up in a locked library and must explore **six interactive objects**, uncover clues, open a combination drawer, collect a brass key, and unlock the exit. This repository demonstrates how a working LLM-led game (Version 1) can be improved into a more reliable AI application (Version 2).

> **Main idea:** In Version 1, the AI is both the **storyteller and referee**. In Version 2, **Python is the referee** and Gemini is an **optional storyteller**.

## Versions

| Feature | Version 1 | Version 2 — Dark Mystery |
|---|---|---|
| Web interface | Streamlit chat | Streamlit chat with antique-gold/dark-library styling |
| AI | Gemini Game Master | Optional Gemini narration of Python-validated events |
| Conversation / progress | AI uses conversation history | Python dictionary stored in `st.session_state` |
| Inventory, lock checks | Governed by LLM instructions | Validated by `engine.py` |
| Winning condition | AI returns `[[ESCAPED]]` marker | Python requires the collected key, key turned, and correct keypad code |
| Invalid actions | LLM may be inconsistent | Python rejects invalid or unauthorized actions |
| Without working Gemini API | Cannot continue gameplay | Core game still works; optional narration is skipped |

The room contains a **desk, bookshelf, painting, clock, locked drawer and exit door**. The three puzzle stages are (1) discover the drawer code, (2) open the drawer and collect the key, and (3) work out the four-digit door code and escape.

## Repository structure

```text
AI-Escape-Room/
├── README.md                     # This portfolio overview
├── .gitignore                    # Keeps private and temporary files out of Git
├── version1/                     # Original LLM-led implementation
│   ├── app.py
│   ├── game_config.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── README.md
│   ├── test_results.md           # Add your real manual test observations
│   └── screenshots/              # Add your captured Version 1 images
├── version2/                     # Python-validated implementation
│   ├── app.py
│   ├── engine.py
│   ├── game_config.py
│   ├── narrator.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── .streamlit/config.toml
│   ├── assets/theme.css
│   ├── README.md
│   ├── test_cases.md
│   ├── tests/test_engine.py
│   └── screenshots/              # Add your captured Version 2 images
└── docs/
    ├── architecture.md
    ├── automated_test_results.md
    └── final_report.pdf
```

If your local folder is named `Escape_Room_V1`, you can **rename it to `version1`** to match this structure. Keep the latest redesigned version in `version2`.

## Run the app (Windows PowerShell)

**Requirements:** Python 3.10+, pip, and optionally a Gemini API key for AI narration.

### Version 1

```powershell
cd version1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` in VS Code and replace the placeholder `GEMINI_API_KEY` with your own key. Choose a `GEMINI_MODEL` available to your key. Then run:

```powershell
py -m streamlit run app.py
```

### Version 2

Stop the first Streamlit server with `Ctrl + C` (or use another port). From the repository root:

```powershell
cd version2
py -m pip install -r requirements.txt
Copy-Item .env.example .env
py -m streamlit run app.py
```

The core Version 2 game works without a Gemini key. To enable the optional atmospheric narrator, edit its local `.env` and add your key and a supported model name.

Both versions normally open at **http://localhost:8501**.

## Example player actions

1. `Examine the desk`
2. `Examine the bookshelf`
3. `Enter 274 on the drawer`
4. `Pick up the brass key`
5. `Examine the painting`
6. `Look at the clock`
7. `Use the brass key on the exit door and enter 0835`

The correct exit requires **both the brass key and the valid door code**.

## Tests and evidence

The Version 2 engine includes 15 automatic `unittest` cases covering successful escape, incorrect combinations, inventory, false player claims, invented objects, admin-role prompt injection, restart and invalid narrator victory claims.

From `version2/`:

```powershell
py -m unittest discover -s tests -v
```

**Verified in the supplied project:** 15 tests passed, 0 failed, 0 errors (15 November 2026). Full details are in [`docs/automated_test_results.md`](docs/automated_test_results.md).

The automatic tests do **not** replace visual/manual testing. Add your real screenshots in both `screenshots/` folders and fill in the observed results in `version1/test_results.md` and `version2/test_cases.md`. Do not mark a manual test as passed unless you actually ran it.

## Architecture and report

- [Version 1 and Version 2 diagrams](docs/architecture.md)
- [Automated test evidence and limitations](docs/automated_test_results.md)
- [Final 3-page project report](docs/final_report.pdf)
- [Version 1 detailed README](version1/README.md)
- [Version 2 detailed README](version2/README.md)

## What improved, and why?

Version 1 provides natural conversation, but the AI has to infer inventory and previous actions from chat history. It may misunderstand a move, invent an object, or inconsistently accept a code. **These are design risks, not claims that every failure occurred during testing.**

Version 2 solves the critical reliability problem by putting the room state, inventory, allowed actions, puzzle answers and victory condition in deterministic Python functions. The UI reads state directly from Python. Gemini receives only a validated event for optional atmosphere; it cannot update the game. The Dark Mystery redesign improves presentation without changing the underlying engine.

## Limitations

- The Version 2 parser supports common English actions, not every possible phrasing.
- Progress is stored for the current Streamlit session; it is not persisted in a database.
- The optional AI narrator can still produce imperfect wording, but it does not control puzzle progress.
- Puzzle answers are visible in source code because this is a reproducible educational demonstration.
- Automated tests cover the engine; human testing is still needed for layout and live API behavior.

## Security and GitHub submission

**Never commit `.env` or real API keys.** Commit `.env.example` as a template. Review `git status` before every commit and exclude virtual environments, caches, and temporary files.

Use meaningful development commits (Version 1 baseline, Version 2 engine, Dark Mystery styling, test documentation), then make the repository public and submit its GitHub link with your assignment.

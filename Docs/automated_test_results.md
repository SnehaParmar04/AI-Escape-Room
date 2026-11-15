# Version 2 — Automated Test Results

## Verified execution

- **Date checked:** 15 November 2026
- **Scope:** The Version 2 Python engine from the current Dark Mystery project (same `engine.py`, `game_config.py`, `narrator.py` and `tests/test_engine.py` as the tested baseline)
- **Command (run inside `version2/`):**

```powershell
py -m unittest discover -s tests -v
```

- **Observed result in the project execution environment:** **15 tests run, 15 passed, 0 failures, 0 errors**.

```text
----------------------------------------------------------------------
Ran 15 tests in 0.003s

OK
```

Runtime may differ on another computer; the assertion results should be checked again before submission.

## What the 15 tests cover

| # | Automated test | Verified result |
|---|---|---|
| 1 | `test_01_full_successful_escape` | PASS |
| 2 | `test_02_wrong_drawer_code_rejected` | PASS |
| 3 | `test_03_cannot_collect_key_before_drawer_open` | PASS |
| 4 | `test_04_cannot_use_key_not_collected` | PASS |
| 5 | `test_05_wrong_door_code_rejected` | PASS |
| 6 | `test_06_admin_prompt_injection_rejected` | PASS |
| 7 | `test_07_false_claim_of_prior_progress_rejected` | PASS |
| 8 | `test_08_request_for_secret_codes_refused` | PASS |
| 9 | `test_09_nonexistent_object_not_created` | PASS |
| 10 | `test_10_door_needs_both_requirements` | PASS |
| 11 | `test_11_remembers_previous_actions` | PASS |
| 12 | `test_12_restart_makes_fresh_state` | PASS |
| 13 | `test_13_no_fake_victory_from_narrator` | PASS |
| 14 | `test_14_collect_and_use_key_in_same_command` | PASS |
| 15 | `test_15_keypad_and_key_in_same_command` | PASS |

## Five representative cases for the professor

| Test situation | Version 1 limitation to investigate | Version 2 verified handling |
|---|---|---|
| Wrong drawer code | The LLM could mistakenly accept the number | Python leaves the drawer locked |
| Key used before collecting it | Chat-based memory could wrongly assume possession | Inventory check rejects key use |
| Administrator claims special authority | LLM could follow an instruction outside the story | Python rejects the bypass attempt |
| Player claims a puzzle is already complete | LLM might accept an unsupported claim | Stored state does not change |
| Victory requested before final puzzle | LLM could announce success too early | Python requires key turned + keypad code accepted |

**Important:** “Version 1 limitation” refers to a **risk to test**, not a claim that every Version 1 attempt actually failed. The assignment asks you to record what you personally observed in `version1/test_results.md`.

## What these tests do not prove

The tests run `engine.py` and narration-safety checks without relying on a live Gemini connection or browser. They **do not** verify visual appearance, all possible natural-language phrases, real Gemini API responses, or the student's screenshot evidence.

### Manual verification still needed

1. Launch both Streamlit versions and capture real gameplay screenshots.
2. Record the observed results for at least five manual scenarios in `version1/test_results.md` and `version2/test_cases.md`.
3. Save the Version 2 terminal test screenshot, e.g. `version2/screenshots/08_automated_tests.png`.
4. Re-run the tests on your laptop and note any differences from the results above.

The final report distinguishes automated evidence from manual observations and unverified risks.

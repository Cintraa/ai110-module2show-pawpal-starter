# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I gave Claude (running as an agent with file and terminal access to this repo) the full PawPal+ assignment: all six phases, from the UML draft through the Streamlit polish, the README and the reflection. The task said the final result mattered more than the route, and it included the key constraints: dataclasses for `Task`/`Pet`, a `Scheduler` that must read through `Owner.get_all_tasks()`, `python -m pytest` must pass, and one commit per phase.

**What did the agent do?**

1. Read the starter repo (`README.md`, `app.py`, `reflection.md`, `diagrams/uml.mmd`) and checked the environment (Python version, installed packages, git remote).
2. Drafted the UML (`diagrams/uml_draft.mmd`) and generated dataclass skeletons in `pawpal_system.py`.
3. Implemented `Task`, `Pet`, `Owner` and `Scheduler`, wrote `main.py`, and ran it in the terminal to check the printed schedule.
4. Added the algorithmic layer (time/priority sorting, filtering, daily/weekly recurrence with `timedelta`, overlap-based conflict detection, free-slot suggestions, time-budget plan) across `pawpal_system.py`, `main.py` and `app.py` in one multi-file change.
5. Wrote 32 pytest tests, ran them, and pasted the real output into the README.
6. Wired `app.py` to the classes with `st.session_state`, and smoke-tested every UI callback with a stand-in for Streamlit.
7. Rendered the final Mermaid diagram to PNG to confirm it parses, then updated the README and reflection and committed each phase separately.

**What did you have to verify or fix manually?**

- Sorting on raw `"HH:MM"` strings breaks for single-digit hours (`"9:00"` sorts after `"10:00"`). The fix was to normalize times in `Task.__post_init__`, plus a regression test.
- The first plan explanation listed reasons in time order, so the "minutes left" numbers jumped around (140, 110, 10, 105…). It was changed to list decisions in the order the greedy algorithm made them.
- Streamlit reruns the whole script on every click, so the agent put every state change (add pet/task, complete, remove, apply fix) in `on_click` callbacks. That way the metrics and tables refresh on the same click instead of one click late.
- The agent's UI check ran without a browser (using a stand-in for Streamlit), so the real UI still needed a manual run of `streamlit run app.py` to confirm the layout.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->

# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🏗️ Implementation summary

All logic lives in `pawpal_system.py`:

- **`Task`** (dataclass): one activity with `description`, `time` (`HH:MM`), `duration_minutes`, `priority`, `frequency`, `completed`, plus the `pet_name` it belongs to and a `task_id`. `mark_complete()` flips its status.
- **`Pet`** (dataclass): pet details and its `tasks`. `add_task()` attaches a task and stamps the pet's name on it; `task_count` reports how many it has.
- **`Owner`** (dataclass): the owner, their daily `available_minutes`, and their `pets`. `add_pet()` rejects duplicate names; `get_all_tasks()` returns every pet's tasks in one list.
- **`Scheduler`**: holds the `Owner` and reads tasks only through `Owner.get_all_tasks()`, so it always sees every pet. `todays_schedule()` returns them in time order.

`main.py` builds an owner with two pets and prints the schedule; `tests/test_pawpal.py` checks task completion and task addition (`python -m pytest`).

## 🖥️ Sample Output

Output of `python main.py`:

```
Today's Schedule for Jordan (2 pets)
========================================
  TIME   PET    TASK                 MIN  PRIORITY STATUS
  -----  -----  ------------------   ---  -------- -------
  07:45  Luna   Breakfast             10  high     pending
  08:00  Mochi  Morning walk          30  high     pending
  14:00  Mochi  Vet checkup           60  high     pending
  17:00  Luna   Play session          20  medium   pending

After completing Luna's breakfast (4 tasks total):
  TIME   PET    TASK                 MIN  PRIORITY STATUS
  -----  -----  ------------------   ---  -------- -------
  07:45  Luna   Breakfast             10  high     done
  08:00  Mochi  Morning walk          30  high     pending
  14:00  Mochi  Vet checkup           60  high     pending
  17:00  Luna   Play session          20  medium   pending
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

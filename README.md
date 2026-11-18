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
PawPal+ | Owner: Jordan | Pets: Mochi, Luna | Daily care budget: 150 min

Today's Schedule (Wed 2026-11-18) - sorted by time
==================================================
  TIME         PET    TASK                MIN  PRIORITY  REPEATS  STATUS
  -----------  -----  ------------------  ---  --------  -------  -------
  07:30-07:40  Mochi  Breakfast            10  high      daily    pending
  07:45-07:55  Luna   Breakfast            10  high      daily    pending
  08:00-08:30  Mochi  Morning walk         30  high      daily    pending
  08:00-08:15  Luna   Brush coat           15  low       weekly   pending
  12:00-12:05  Luna   Thyroid medication    5  high      daily    pending
  14:00-15:00  Mochi  Vet checkup          60  high      once     pending
  17:00-17:20  Luna   Play session         20  medium    daily    pending
  18:30-19:00  Mochi  Evening walk         30  medium    daily    pending

Sorted by priority (high first, ties by time)
=============================================
  TIME         PET    TASK                MIN  PRIORITY  REPEATS  STATUS
  -----------  -----  ------------------  ---  --------  -------  -------
  07:30-07:40  Mochi  Breakfast            10  high      daily    pending
  07:45-07:55  Luna   Breakfast            10  high      daily    pending
  08:00-08:30  Mochi  Morning walk         30  high      daily    pending
  12:00-12:05  Luna   Thyroid medication    5  high      daily    pending
  14:00-15:00  Mochi  Vet checkup          60  high      once     pending
  17:00-17:20  Luna   Play session         20  medium    daily    pending
  18:30-19:00  Mochi  Evening walk         30  medium    daily    pending
  08:00-08:15  Luna   Brush coat           15  low       weekly   pending

Filter: Mochi's tasks (all dates)
=================================
  DATE        TIME         PET    TASK                MIN  PRIORITY  REPEATS  STATUS
  ----------  -----------  -----  ------------------  ---  --------  -------  -------
  2026-11-18  07:30-07:40  Mochi  Breakfast            10  high      daily    pending
  2026-11-18  08:00-08:30  Mochi  Morning walk         30  high      daily    pending
  2026-11-18  14:00-15:00  Mochi  Vet checkup          60  high      once     pending
  2026-11-18  18:30-19:00  Mochi  Evening walk         30  medium    daily    pending
  2026-11-19  10:00-10:45  Mochi  Grooming             45  medium    once     pending

Conflict check
==============
  WARNING: Conflict for Mochi and Luna: 'Morning walk' (08:00-08:30) overlaps 'Brush coat' (08:00-08:15).
  Suggestion: move Luna's 'Brush coat' to 08:30 (next free slot).

Recurring tasks: completing Mochi's daily breakfast
===================================================
  Marked 'Breakfast' (2026-11-18) complete -> completed=True
  Auto-created next daily occurrence: 'Breakfast' on 2026-11-19 at 07:30

Filter: pending tasks today
===========================
  TIME         PET    TASK                MIN  PRIORITY  REPEATS  STATUS
  -----------  -----  ------------------  ---  --------  -------  -------
  07:45-07:55  Luna   Breakfast            10  high      daily    pending
  08:00-08:30  Mochi  Morning walk         30  high      daily    pending
  08:00-08:15  Luna   Brush coat           15  low       weekly   pending
  12:00-12:05  Luna   Thyroid medication    5  high      daily    pending
  14:00-15:00  Mochi  Vet checkup          60  high      once     pending
  17:00-17:20  Luna   Play session         20  medium    daily    pending
  18:30-19:00  Mochi  Evening walk         30  medium    daily    pending

Tomorrow's Schedule (Thu 2026-11-19)
====================================
  TIME         PET    TASK                MIN  PRIORITY  REPEATS  STATUS
  -----------  -----  ------------------  ---  --------  -------  -------
  07:30-07:40  Mochi  Breakfast            10  high      daily    pending
  10:00-10:45  Mochi  Grooming             45  medium    once     pending

Daily plan: 140 of 150 min used
===============================
  TIME         PET    TASK                MIN  PRIORITY  REPEATS  STATUS
  -----------  -----  ------------------  ---  --------  -------  -------
  07:45-07:55  Luna   Breakfast            10  high      daily    pending
  08:00-08:30  Mochi  Morning walk         30  high      daily    pending
  08:00-08:15  Luna   Brush coat           15  low       weekly   pending
  12:00-12:05  Luna   Thyroid medication    5  high      daily    pending
  14:00-15:00  Mochi  Vet checkup          60  high      once     pending
  17:00-17:20  Luna   Play session         20  medium    daily    pending

  Why:
   - Placed Luna's Breakfast (07:45): high priority, 10 min fits (140 min left).
   - Placed Mochi's Morning walk (08:00): high priority, 30 min fits (110 min left).
   - Placed Luna's Thyroid medication (12:00): high priority, 5 min fits (105 min left).
   - Placed Mochi's Vet checkup (14:00): high priority, 60 min fits (45 min left).
   - Placed Luna's Play session (17:00): medium priority, 20 min fits (25 min left).
   - Skipped Mochi's Evening walk (18:30): medium priority, needs 30 min but only 25 min left.
   - Placed Luna's Brush coat (08:00): low priority, 15 min fits (10 min left).
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

## 🧠 Smarter Scheduling

| Feature | Method(s) | How it works |
|---------|-----------|--------------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | `sorted()` with a `lambda` key: `(due_date, time)` for chronological order; `(-priority_rank, due_date, time)` for priority order. `Task.__post_init__` zero-pads times so `"9:00"` can't sort after `"10:00"`. |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.get_tasks_for_date()`, `Scheduler.todays_schedule()` | Optional `pet_name` (case-insensitive) and `completed` filters that can be combined; date filtering keeps tomorrow's recurring copies out of today's view. |
| Conflict handling | `Scheduler.find_conflicts()`, `Scheduler.detect_conflicts()`, `Task.overlaps()` | Sort the day's pending tasks by start, then sweep: compare each task only with tasks that start before it ends. Overlap rule: `a.start < b.end and b.start < a.end`, so back-to-back tasks (08:00–08:30 then 08:30) are fine. Returns warning strings instead of raising. |
| Conflict fixes | `Scheduler.suggest_reschedule()`, `Scheduler.find_next_free_slot()`, `Task.reschedule()` | Moves the lower-priority task of a pair (ties: the later one) to the earliest gap long enough for it, between 06:00 and 22:00. |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Task.next_occurrence()` | Marks the task done; for `daily`/`weekly` uses `timedelta` to create a fresh pending copy on the next due date with a new `task_id`. Completing the same task twice does not create duplicates. |
| Time-budget plan | `Scheduler.generate_daily_plan()`, `DailyPlan.explain()` | Greedy: walk pending tasks in priority order, place each one that still fits the owner's `available_minutes`, skip the rest, then show the placed tasks in time order with reasons. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

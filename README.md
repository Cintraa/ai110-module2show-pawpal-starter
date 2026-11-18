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
python -m pytest
```

The suite in `tests/test_pawpal.py` (32 tests) covers:

- **Basics:** `mark_complete()` flips status; `Pet.add_task()` increases the task count and stamps the pet name.
- **Validation:** time normalization and rejection of bad times, priorities, frequencies, durations and blank descriptions.
- **Multi-pet access:** `Owner.get_all_tasks()` spans every pet; duplicate pet names are rejected; a pet with no tasks yields an empty schedule, no conflicts and an empty plan.
- **Sorting correctness:** chronological order across pets, single-digit hours (`9:00` vs `10:00`), date-before-time ordering, and priority ordering with time tie-breaks.
- **Filtering:** by pet (case-insensitive), by completion status, combined, and by date.
- **Recurrence:** daily → next day, weekly → +7 days, one-off → nothing, and no duplicates when completing twice.
- **Conflict detection:** identical start times across pets, overlapping durations for the same pet, back-to-back tasks *not* flagged, completed/other-day tasks ignored, every pair reported in a three-way clash, the reschedule suggestion resolves the clash, and a full day returns no free slot.
- **Daily plan:** respects the time budget, places high priority first, and explains every decision.

Sample run:

```
============================= test session starts ==============================
platform linux -- Python 3.13.18, pytest-9.1.1, pluggy-1.6.0 -- /usr/local/bin/python3
rootdir: /tmp/ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
plugins: platformdirs-4.13.5, anyio-4.15.1
collecting ... collected 32 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  3%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [  6%]
tests/test_pawpal.py::test_time_is_normalized_to_zero_padded_hhmm PASSED [  9%]
tests/test_pawpal.py::test_invalid_task_fields_raise_value_error[hour-25] PASSED [ 12%]
tests/test_pawpal.py::test_invalid_task_fields_raise_value_error[am-pm-format] PASSED [ 15%]
tests/test_pawpal.py::test_invalid_task_fields_raise_value_error[unknown-priority] PASSED [ 18%]
tests/test_pawpal.py::test_invalid_task_fields_raise_value_error[unknown-frequency] PASSED [ 21%]
tests/test_pawpal.py::test_invalid_task_fields_raise_value_error[zero-duration] PASSED [ 25%]
tests/test_pawpal.py::test_invalid_task_fields_raise_value_error[blank-description] PASSED [ 28%]
tests/test_pawpal.py::test_get_all_tasks_collects_tasks_from_every_pet PASSED [ 31%]
tests/test_pawpal.py::test_duplicate_pet_names_are_rejected PASSED       [ 34%]
tests/test_pawpal.py::test_pet_with_no_tasks_produces_empty_results PASSED [ 37%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 40%]
tests/test_pawpal.py::test_sort_by_time_handles_single_digit_hours PASSED [ 43%]
tests/test_pawpal.py::test_sort_by_time_orders_by_date_first PASSED      [ 46%]
tests/test_pawpal.py::test_sort_by_priority_puts_high_first_and_breaks_ties_by_time PASSED [ 50%]
tests/test_pawpal.py::test_filter_by_pet_name_is_case_insensitive PASSED [ 53%]
tests/test_pawpal.py::test_filter_by_completion_status PASSED            [ 56%]
tests/test_pawpal.py::test_filter_by_pet_and_status_combined PASSED      [ 59%]
tests/test_pawpal.py::test_todays_schedule_excludes_other_dates PASSED   [ 62%]
tests/test_pawpal.py::test_completing_daily_task_creates_task_for_next_day PASSED [ 65%]
tests/test_pawpal.py::test_completing_weekly_task_creates_task_one_week_later PASSED [ 68%]
tests/test_pawpal.py::test_completing_one_off_task_creates_nothing PASSED [ 71%]
tests/test_pawpal.py::test_completing_same_task_twice_does_not_duplicate PASSED [ 75%]
tests/test_pawpal.py::test_detects_duplicate_times_across_pets PASSED    [ 78%]
tests/test_pawpal.py::test_detects_overlapping_durations_for_same_pet PASSED [ 81%]
tests/test_pawpal.py::test_back_to_back_tasks_do_not_conflict PASSED     [ 84%]
tests/test_pawpal.py::test_conflicts_ignore_completed_tasks_and_other_days PASSED [ 87%]
tests/test_pawpal.py::test_three_way_overlap_reports_every_pair PASSED   [ 90%]
tests/test_pawpal.py::test_suggest_reschedule_moves_lower_priority_task_to_next_free_slot PASSED [ 93%]
tests/test_pawpal.py::test_find_next_free_slot_returns_none_when_day_is_full PASSED [ 96%]
tests/test_pawpal.py::test_daily_plan_respects_time_budget_and_priority PASSED [100%]

============================== 32 passed in 0.07s ==============================
```

**Confidence level: ★★★★☆ (4/5).** Every scheduling rule has happy-path and edge-case tests, and the CLI demo exercises the same code end to end. One star is held back because the Streamlit UI was smoke-tested by hand rather than by automated UI tests, and a few edge cases are knowingly out of scope (tasks that cross midnight, overdue recurring tasks, persistence between sessions).

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

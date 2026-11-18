# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions a user should be able to perform:

1. **Add a pet:** register each pet (name, species, age) under one owner.
2. **Schedule a care task for a pet:** say what needs to happen, at what time, for how long, how important it is, and whether it repeats (daily/weekly).
3. **See today's schedule:** one combined, time-ordered list across all pets, with warnings when two things clash and a plan that fits the time I actually have.

My initial UML (`diagrams/uml_draft.mmd`) had four classes:

- **`Task`**: one activity. Holds `description`, `time` ("HH:MM"), `duration_minutes`, `priority`, `frequency` and `completed`. Its only behavior is `mark_complete()`.
- **`Pet`**: pet details (`name`, `species`, `age`) plus its list of tasks; it can `add_task()` and `get_tasks()`.
- **`Owner`**: the person, a daily time budget (`available_minutes`) and a list of pets; it can `add_pet()` and `get_all_tasks()` (every pet's tasks in one list).
- **`Scheduler`**: the "brain." It holds a reference to the `Owner` and reads tasks only through `get_all_tasks()`, then sorts, filters, detects conflicts and builds a daily plan.

Relationships: an Owner *has* many Pets (aggregation), a Pet *has* many Tasks (composition), and the Scheduler *uses* the Owner. I used dataclasses for `Task`, `Pet` and `Owner` because they are mostly data with a few methods. `Scheduler` is a regular class because it is behavior wrapped around an owner.

**b. Design changes**

Yes. Reviewing the skeleton (with AI) before writing logic, and then building the algorithms, exposed a few gaps:

- **Added `due_date` to `Task`.** Recurring tasks need a date. Without one, "tomorrow's walk" and "today's walk" are indistinguishable, and today's schedule would fill up with future copies.
- **Added `task_id`.** Two tasks can share a description ("Breakfast" for both pets), and the Streamlit UI needs a stable way to say *which* task to complete, remove or move.
- **Added a `pet_name` back-reference, stamped by `Pet.add_task()`.** The Scheduler works on the flat list from `Owner.get_all_tasks()`, so each task needs to know its pet for filtering and warning messages. I deliberately stored the *name* instead of a `Pet` object. A `Pet` holds its `Task`s, so a `Task → Pet` object link would make the auto-generated dataclass `__repr__`/`__eq__` recurse forever.
- **Recurrence is split across two classes.** `Task.next_occurrence()` only knows how to copy itself onto the next date; `Scheduler.mark_task_complete()` decides when to call it and which pet gets the copy. That keeps `Task` unaware of pets.
- **Added a `DailyPlan` result class.** Returning a bare list from `generate_daily_plan()` lost the skipped tasks and the reasons, which the UI needs to explain the plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers:

- **Time of day and duration:** every task has a start (`HH:MM`) and a length, which define its time window for sorting and overlap checks.
- **Date:** only tasks due on the selected day are scheduled or checked for conflicts.
- **Priority (high / medium / low):** decides what goes into the plan first and which task to move when two clash.
- **The owner's time budget (`available_minutes`):** the hard limit for the daily plan.
- **Completion status:** finished tasks don't conflict and aren't planned again.

I ranked them by "what hurts the pet most if it's missed." Feeding and medication are tagged high priority and must be placed first; the time budget is the real-world hard constraint; exact clock times matter mainly for spotting double-booking. Owner preferences are currently limited to the time budget.

**b. Tradeoffs**

- **Conflicts are warnings, not auto-fixes, and they use overlapping durations rather than exact time matches.** `detect_conflicts()` flags any two pending tasks whose windows overlap (`a.start < b.end and b.start < a.end`), even for *different* pets. That treats the owner as a single resource, so it can over-warn: you can refill the cat's water while the dog eats. I think that's the right trade for this scenario. A false alarm costs a glance, a missed clash can mean a skipped medication, and the owner keeps the final say: the UI suggests a move (`suggest_reschedule()`) but never moves anything on its own.
- **The daily plan is greedy, not optimal.** `generate_daily_plan()` takes tasks in priority order and places each one that still fits the budget. In the demo, the 30-minute medium-priority evening walk is skipped while a 15-minute low-priority brushing still fits in the leftover time. An exact "knapsack" search could squeeze in more minutes, but it's harder to explain and overkill for a handful of tasks per day. The greedy version runs in O(n log n) and produces a one-line reason for every decision.
- **Recurrence is anchored to the task's due date**, not to when I clicked "complete." A weekly Monday task finished on Wednesday comes back next Monday, which keeps routines on their usual days.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude as my AI coding assistant:

- **Phase 1 (design):** brainstormed the four classes and their attributes and methods, generated the Mermaid diagram (`diagrams/uml_draft.mmd`), and turned it into dataclass skeletons. Then I had the AI review the skeleton for missing relationships, which is where `pet_name`, `task_id` and later `due_date` came from.
- **Phase 2 (core):** fleshed out the four classes, built `main.py` as a CLI testing ground, and added the first two tests. The question "how should the Scheduler get tasks from the Owner?" settled the rule that it reads only through `Owner.get_all_tasks()`.
- **Phase 3 (UI bridge):** wired `app.py` to the classes, using `st.session_state` to keep the Owner alive across Streamlit's reruns.
- **Phase 4 (algorithms):** got a list of small algorithm ideas first, then added sorting, filtering, recurrence (with `timedelta`) and conflict detection one at a time, and finished with a simplification pass.
- **Phase 5 (testing):** asked for a test plan covering happy paths and edge cases before writing the suite.
- **Phase 6 (polish):** surfaced the Scheduler's features in the UI, updated the UML to match the final code, and drafted the README features list and walkthrough.

The prompts that worked best gave the AI the full context first, then asked for one narrow thing. The context was the assignment spec, the existing files, and the rule that the Scheduler must read through the Owner. That's context engineering in practice. Examples:

- "Review this skeleton: are any relationships missing, and where would the logic bottleneck?"
- "Based on my skeletons, how should the Scheduler retrieve all tasks from the Owner's pets?"
- "What are the most important edge cases to test for a pet scheduler with sorting and recurring tasks?"
- "How could this algorithm be simplified for better readability or performance?"

**b. Judgment and verification**

- **Sorting on raw strings.** The first `todays_schedule()` in Phase 2 sorted with `key=lambda t: t.time`. That's fine for `"08:00"` but breaks for `"9:00"` vs `"10:00"`, because strings compare character by character. In Phase 4, instead of parsing times inside every sort, times get normalized once in `Task.__post_init__` (which also validates them). `test_sort_by_time_handles_single_digit_hours` locks the fix in.
- **The plan's explanation.** The first daily-plan output listed its reasons in time order, so the "minutes left" numbers jumped around (140, 110, 10, 105…) and made no sense to read. Seeing that in the demo output led to the change: the explanation now follows the order in which the greedy algorithm made its decisions.
- **Conflict detection.** The simplification pass on `find_conflicts()` offered a one-liner: `[(a, b) for a, b in combinations(tasks, 2) if a.overlaps(b)]`. It's shorter and very Pythonic, but it compares every pair. I kept the sorted sweep with an early `break` (comments explain it) because it's still readable, only compares tasks that could actually overlap, and returns clashes in time order. I did keep the idea of an `overlaps()` method on `Task` so the rule lives in one place.
- **Verification.** Every phase was checked before moving on: `python main.py` after each phase to read the printed schedule, `python -m pytest` after every logic change (32 passing), and a click-through of the Streamlit flows (add pet, duplicate pet, overlapping task, apply fix, complete a recurring task, filters, plan, reset).

---

## 4. Testing and Verification

**a. What you tested**

- Task completion and task addition (the Phase 2 basics).
- Input validation (bad times, priorities, frequencies, durations, blank text) and time normalization.
- Multi-pet retrieval through `Owner.get_all_tasks()`, duplicate pet names, and a pet with no tasks.
- Sorting: chronological across pets, single-digit hours, date before time, and priority with time tie-breaks.
- Filtering by pet, status, both, and date.
- Recurrence: daily, weekly, one-off, and completing the same task twice.
- Conflicts: same start time, overlapping durations, back-to-back (not a conflict), completed/other-day tasks ignored, three-way clashes, the reschedule suggestion, and a fully booked day.
- The time-budget plan.

These matter because they are exactly the places where a scheduler silently gives wrong answers instead of crashing: a sort that's *almost* right, a recurring task that duplicates itself, or a clash that goes unnoticed.

**b. Confidence**

4 out of 5. Every scheduling rule has happy-path and edge-case tests, and the CLI demo runs the same code end to end. With more time I'd test:

- tasks that cross midnight (e.g., 23:30 for 60 minutes),
- completing an *overdue* recurring task (should it jump to tomorrow instead of due date + 1?),
- automated UI tests with Streamlit's `AppTest`,
- larger task lists, to confirm the sweep stays fast.

---

## 5. Reflection

**a. What went well**

The separation between the logic layer and the UI. Because every rule lives in `pawpal_system.py` and the Scheduler reads through one Owner method, the CLI demo, the tests and the Streamlit app all exercise the same code. Adding the conflict-fix button to the UI took a few lines because `suggest_reschedule()` already existed and was tested.

**b. What you would improve**

- Persist pets and tasks (save/load JSON) so data survives closing the browser.
- Make the planner smarter: respect time windows ("walk between 7 and 9") and real owner preferences, not just a minute budget.
- Add an "edit task" form instead of remove + re-add.
- Decide on a clearer policy for overdue recurring tasks.

**c. Key takeaway**

The AI writes code faster than I can review it, so my job as the lead architect is to define the boundaries, check the edge cases, and verify. That means deciding what each class owns, which object talks to which, and what "correct" means, then holding every suggestion to that. The best results came from giving the AI precise context and small, verifiable asks, and from never accepting a change until a test or the demo output proved it.

---

## 6. AI Strategy

- **Most effective AI features:** Generating the Mermaid diagram from the class list.
- **A suggestion I rejected or modified:** storing a `Pet` object on each `Task`. It looked convenient, but the two dataclasses would reference each other and their auto-generated `repr`/`eq` would recurse. A `pet_name` string does the job instead (see 1b). The raw-string sort and the `combinations()` one-liner were also modified rather than taken as-is (see 3b).
- **Separate sessions per phase:** each phase was its own focused stage: one goal (design, core, UI bridge, algorithms, tests, polish), one verification step, and one commit, so the git log reads phase by phase. Keeping them separate meant the AI wasn't juggling UI details while working on algorithms, and when something looked off I knew which phase had introduced it.
- **Being the lead architect:** AI is a powerful generator, but it doesn't own the design. The structure was my call: four classes, and the Scheduler reads only through the Owner. So were the tradeoffs: warn instead of auto-fix, and a greedy plan. Every feature claim in the README had to be backed by a test or real output.

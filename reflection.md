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

I used an AI coding assistant (Claude) in agent mode for the whole build. That covered brainstorming the classes, generating the Mermaid UML, turning the UML into dataclass skeletons, implementing the logic, writing the tests, wiring the Streamlit UI, and drafting documentation. The most effective prompts gave it the **full context** up front: the assignment spec, the constraint that the Scheduler must read through `Owner.get_all_tasks()`, and the existing files. Then they asked for one narrow thing at a time. Prompts that helped most:

- "Review this skeleton: are any relationships missing, and where would the logic bottleneck?" (this led to `due_date`, `task_id` and `pet_name`)
- "How should the Scheduler retrieve all tasks from the Owner's pets?"
- "What are the most important edge cases to test for a pet scheduler with sorting and recurring tasks?"
- "How could this algorithm be simplified for better readability or performance?"

**b. Judgment and verification**

- **Sorting on raw strings.** The first `sort_by_time()` suggestion was `sorted(tasks, key=lambda t: t.time)`. That's fine for `"08:00"` but breaks for `"9:00"` vs `"10:00"`, because strings compare character by character. Instead of switching the key to a parsed time everywhere, I normalized times once in `Task.__post_init__` (which also validates them). I locked the fix in with `test_sort_by_time_handles_single_digit_hours`.
- **Conflict detection.** When I asked how to simplify `find_conflicts()`, the suggestion was a one-liner: `[(a, b) for a, b in combinations(tasks, 2) if a.overlaps(b)]`. It's shorter and very Pythonic, but it compares every pair. I kept the sorted sweep with an early `break` (comments explain it) because it's still readable, only compares tasks that could actually overlap, and returns clashes in time order. I did keep the AI's idea of an `overlaps()` method on `Task` so the rule lives in one place.
- **Verification.** I ran `python main.py` after each phase to check the printed schedule by eye, ran `python -m pytest` (32 passing tests) after every logic change, and clicked through every Streamlit flow (add pet, duplicate pet, add overlapping task, apply fix, complete a recurring task, filters, plan, reset).

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

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

Yes. Before writing any logic I asked the AI to review the skeleton for missing relationships and bottlenecks. It flagged gaps that I'm carrying into implementation:

- **Tasks need to know their pet.** The Scheduler works on the flat list from `Owner.get_all_tasks()`, so each task needs a `pet_name` (stamped by `Pet.add_task()`) for filtering and messages. I chose a name string over a `Pet` object reference: a `Pet` holds its `Task`s, so a two-way object link would make the dataclass `__repr__`/`__eq__` recurse.
- **Tasks need a stable id.** Two pets can both have "Breakfast," so the UI will need a `task_id` to pick the right one.
- **Recurrence will need a date on `Task`.** Deferred to the algorithm phase, since the skeleton doesn't schedule across days yet.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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

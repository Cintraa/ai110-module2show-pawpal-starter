"""PawPal+ logic layer.

Four core classes live here:

* ``Task``      - one pet-care activity (what, when, how long, how often, done?).
* ``Pet``       - a pet and the list of tasks that belong to it.
* ``Owner``     - a person who owns several pets; exposes every task via ``get_all_tasks``.
* ``Scheduler`` - the "brain": reads tasks from the Owner and sorts, filters,
                  detects conflicts, handles recurrence, and builds a daily plan.

``DailyPlan`` is a small result object returned by ``Scheduler.generate_daily_plan``.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from typing import Optional

# Higher number = more important. Used for priority sorting and the daily plan.
PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}
VALID_FREQUENCIES = ("once", "daily", "weekly")
FREQUENCY_STEP = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


def _new_id() -> str:
    """Return a short unique id for a task."""
    return uuid.uuid4().hex[:8]


def normalize_time(value: str) -> str:
    """Validate a 24-hour 'H:MM' / 'HH:MM' string and return it zero-padded as 'HH:MM'."""
    try:
        return datetime.strptime(str(value).strip(), "%H:%M").strftime("%H:%M")
    except ValueError as exc:
        raise ValueError(f"Invalid time {value!r}: expected 24-hour HH:MM, e.g. '08:30'.") from exc


def hhmm_to_minutes(value: str) -> int:
    """Convert an 'HH:MM' string into minutes after midnight."""
    hours, minutes = map(int, normalize_time(value).split(":"))
    return hours * 60 + minutes


def minutes_to_hhmm(total_minutes: int) -> str:
    """Convert minutes after midnight into an 'HH:MM' string (wraps past midnight)."""
    total_minutes %= 24 * 60
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


# --------------------------------------------------------------------------- #
# Task
# --------------------------------------------------------------------------- #
@dataclass
class Task:
    """A single pet-care activity scheduled at a time of day on a given date."""

    description: str
    time: str  # 24-hour "HH:MM"
    duration_minutes: int = 15
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "once"  # "once" | "daily" | "weekly"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""  # filled in by Pet.add_task
    task_id: str = field(default_factory=_new_id)

    def __post_init__(self) -> None:
        """Validate and normalize fields so sorting and comparisons stay reliable."""
        self.description = self.description.strip()
        if not self.description:
            raise ValueError("Task description cannot be empty.")
        self.time = normalize_time(self.time)
        self.priority = self.priority.strip().lower()
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"Priority must be one of {list(PRIORITY_RANK)}, got {self.priority!r}.")
        self.frequency = self.frequency.strip().lower()
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"Frequency must be one of {list(VALID_FREQUENCIES)}, got {self.frequency!r}.")
        if int(self.duration_minutes) <= 0:
            raise ValueError("Duration must be a positive number of minutes.")
        self.duration_minutes = int(self.duration_minutes)

    @property
    def start_minutes(self) -> int:
        """Start time as minutes after midnight."""
        return hhmm_to_minutes(self.time)

    @property
    def end_minutes(self) -> int:
        """End time as minutes after midnight (start + duration)."""
        return self.start_minutes + self.duration_minutes

    @property
    def end_time(self) -> str:
        """End time formatted as 'HH:MM'."""
        return minutes_to_hhmm(self.end_minutes)

    @property
    def is_recurring(self) -> bool:
        """True for daily or weekly tasks."""
        return self.frequency in FREQUENCY_STEP

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Undo a completion (mark the task as pending again)."""
        self.completed = False

    def reschedule(self, new_time: str) -> None:
        """Move the task to a new 'HH:MM' start time (validated)."""
        self.time = normalize_time(new_time)

    def next_occurrence(self) -> Optional[Task]:
        """Return a fresh, pending copy of a recurring task on its next due date (None if one-off)."""
        step = FREQUENCY_STEP.get(self.frequency)
        if step is None:
            return None
        return replace(self, due_date=self.due_date + step, completed=False, task_id=_new_id())

    def overlaps(self, other: Task) -> bool:
        """True if both tasks are on the same date and their time windows overlap."""
        return (
            self.due_date == other.due_date
            and self.start_minutes < other.end_minutes
            and other.start_minutes < self.end_minutes
        )

    def summary(self) -> str:
        """One-line human readable description of the task."""
        status = "done" if self.completed else "pending"
        return (
            f"{self.time}-{self.end_time} {self.pet_name or '?'}: {self.description} "
            f"({self.duration_minutes} min, {self.priority}, {self.frequency}, {status})"
        )


# --------------------------------------------------------------------------- #
# Pet
# --------------------------------------------------------------------------- #
@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str = "dog"
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the pet's name."""
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Pet name cannot be empty.")

    def add_task(self, task: Task) -> Task:
        """Attach a task to this pet (stamping the pet's name on it) and return it."""
        task.pet_name = self.name
        self.tasks.append(task)
        return task

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by id; return True if something was removed."""
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.task_id != task_id]
        return len(self.tasks) < before

    def get_tasks(self, include_completed: bool = True) -> list[Task]:
        """Return this pet's tasks, optionally hiding completed ones."""
        return [t for t in self.tasks if include_completed or not t.completed]

    @property
    def task_count(self) -> int:
        """Number of tasks attached to this pet."""
        return len(self.tasks)


# --------------------------------------------------------------------------- #
# Owner
# --------------------------------------------------------------------------- #
@dataclass
class Owner:
    """A pet owner who manages several pets and a daily time budget for pet care."""

    name: str
    available_minutes: int = 120
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> Pet:
        """Add a pet; pet names must be unique per owner (case-insensitive)."""
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"{self.name} already has a pet named {pet.name!r}.")
        self.pets.append(pet)
        return pet

    def remove_pet(self, name: str) -> bool:
        """Remove a pet (and its tasks) by name; return True if removed."""
        before = len(self.pets)
        self.pets = [p for p in self.pets if p.name.lower() != name.strip().lower()]
        return len(self.pets) < before

    def get_pet(self, name: str) -> Optional[Pet]:
        """Find a pet by name (case-insensitive), or None."""
        wanted = name.strip().lower()
        return next((p for p in self.pets if p.name.lower() == wanted), None)

    def get_all_tasks(self) -> list[Task]:
        """Return every task from every pet in one flat list."""
        return [task for pet in self.pets for task in pet.tasks]

    def find_task(self, task_id: str) -> Optional[Task]:
        """Look up any of the owner's tasks by id, or None."""
        return next((t for t in self.get_all_tasks() if t.task_id == task_id), None)


# --------------------------------------------------------------------------- #
# Scheduler
# --------------------------------------------------------------------------- #
@dataclass
class DailyPlan:
    """Result of Scheduler.generate_daily_plan: what fits today, what doesn't, and why."""

    day: date
    minutes_available: int
    scheduled: list[Task] = field(default_factory=list)  # chronological order
    skipped: list[Task] = field(default_factory=list)
    decisions: list[tuple[Task, bool, str]] = field(default_factory=list)  # (task, placed?, reason) in decision order

    @property
    def minutes_used(self) -> int:
        """Total minutes of the scheduled tasks."""
        return sum(t.duration_minutes for t in self.scheduled)

    def explain(self) -> list[str]:
        """Human-readable reasoning, one line per task, in the order the scheduler decided."""
        return [
            f"{'Placed' if placed else 'Skipped'} {t.pet_name}'s {t.description} ({t.time}): {reason}"
            for t, placed, reason in self.decisions
        ]


class Scheduler:
    """The 'brain' of PawPal+: organizes every pet's tasks through Owner.get_all_tasks()."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that works on one owner's pets."""
        self.owner = owner

    # ---- retrieval -------------------------------------------------------- #
    def get_all_tasks(self) -> list[Task]:
        """All tasks across all of the owner's pets."""
        return self.owner.get_all_tasks()

    def get_tasks_for_date(self, day: Optional[date] = None, include_completed: bool = True) -> list[Task]:
        """Tasks due on a given date (default today)."""
        day = day or date.today()
        return [
            t for t in self.get_all_tasks()
            if t.due_date == day and (include_completed or not t.completed)
        ]

    # ---- sorting ---------------------------------------------------------- #
    def sort_by_time(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks in chronological order (date, then HH:MM start time).

        Times are normalized to zero-padded "HH:MM" in Task.__post_init__, so the
        string key sorts correctly ("09:00" < "10:00").
        """
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: (t.due_date, t.time))

    def sort_by_priority(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks with high priority first; ties are broken by start time."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: (-PRIORITY_RANK[t.priority], t.due_date, t.time))

    # ---- filtering -------------------------------------------------------- #
    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        tasks: Optional[list[Task]] = None,
    ) -> list[Task]:
        """Filter by pet name (case-insensitive) and/or completion status; None means 'any'."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        if pet_name:
            wanted = pet_name.strip().lower()
            tasks = [t for t in tasks if t.pet_name.lower() == wanted]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def todays_schedule(self, day: Optional[date] = None, include_completed: bool = True) -> list[Task]:
        """Tasks due on a date (default today), sorted by start time."""
        return self.sort_by_time(self.get_tasks_for_date(day, include_completed))

    # ---- recurrence ------------------------------------------------------- #
    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task; for daily/weekly tasks, add and return the next occurrence."""
        if task.completed:  # completing twice must not spawn duplicate follow-ups
            return None
        task.mark_complete()
        follow_up = task.next_occurrence()
        if follow_up is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is None:
                raise ValueError(f"Task {task.description!r} is not attached to one of {self.owner.name}'s pets.")
            pet.add_task(follow_up)
        return follow_up

    # ---- conflicts -------------------------------------------------------- #
    def find_conflicts(self, day: Optional[date] = None) -> list[tuple[Task, Task]]:
        """Return pairs of pending tasks on the same day whose time windows overlap.

        Sweep approach: sort by start time, then compare each task only with the
        tasks that start before it ends - O(n log n) plus the number of overlaps.
        """
        tasks = sorted(self.get_tasks_for_date(day, include_completed=False), key=lambda t: t.start_minutes)
        pairs: list[tuple[Task, Task]] = []
        for i, first in enumerate(tasks):
            for second in tasks[i + 1:]:
                if not first.overlaps(second):
                    break  # sorted by start, so no later task can overlap `first` either
                pairs.append((first, second))
        return pairs

    def detect_conflicts(self, day: Optional[date] = None) -> list[str]:
        """Return readable warning messages for overlapping tasks (empty list = no conflicts).

        Lightweight by design: it never raises and never moves tasks, it only warns.
        """
        warnings = []
        for a, b in self.find_conflicts(day):
            who = f"same pet ({a.pet_name})" if a.pet_name == b.pet_name else f"{a.pet_name} and {b.pet_name}"
            warnings.append(
                f"Conflict for {who}: '{a.description}' ({a.time}-{a.end_time}) overlaps "
                f"'{b.description}' ({b.time}-{b.end_time})."
            )
        return warnings

    def find_next_free_slot(
        self,
        duration_minutes: int,
        day: Optional[date] = None,
        earliest: str = "06:00",
        latest: str = "22:00",
        exclude_task_id: Optional[str] = None,
    ) -> Optional[str]:
        """Earliest 'HH:MM' start between `earliest` and `latest` where a task of this length fits.

        Walks the day's pending tasks in start order, pushing a cursor past each busy
        window until a gap is big enough. `exclude_task_id` ignores the task being moved.
        Returns None when nothing fits before `latest`.
        """
        cursor = hhmm_to_minutes(earliest)
        limit = hhmm_to_minutes(latest)
        busy = [t for t in self.get_tasks_for_date(day, include_completed=False) if t.task_id != exclude_task_id]
        for task in sorted(busy, key=lambda t: t.start_minutes):
            if task.start_minutes - cursor >= duration_minutes:
                break  # the gap before this task is big enough
            cursor = max(cursor, task.end_minutes)
        return minutes_to_hhmm(cursor) if cursor + duration_minutes <= limit else None

    def suggest_reschedule(self, first: Task, second: Task) -> Optional[tuple[Task, str]]:
        """For a conflicting pair, pick the task to move (lower priority; ties move the later one)
        and the next free start time for it. Returns None if no slot is free today."""
        mover = second if PRIORITY_RANK[second.priority] <= PRIORITY_RANK[first.priority] else first
        slot = self.find_next_free_slot(
            mover.duration_minutes, mover.due_date, earliest=mover.time, exclude_task_id=mover.task_id
        )
        return (mover, slot) if slot else None

    # ---- planning --------------------------------------------------------- #
    def generate_daily_plan(self, day: Optional[date] = None) -> DailyPlan:
        """Greedy plan: take pending tasks by priority (then time) until the owner's time budget is used.

        The chosen tasks are returned in chronological order with a reason for each,
        plus the tasks that did not fit.
        """
        day = day or date.today()
        plan = DailyPlan(day=day, minutes_available=self.owner.available_minutes)
        remaining = self.owner.available_minutes
        for task in self.sort_by_priority(self.get_tasks_for_date(day, include_completed=False)):
            if task.duration_minutes <= remaining:
                remaining -= task.duration_minutes
                plan.scheduled.append(task)
                plan.decisions.append(
                    (task, True, f"{task.priority} priority, {task.duration_minutes} min fits ({remaining} min left).")
                )
            else:
                plan.skipped.append(task)
                plan.decisions.append(
                    (task, False, f"{task.priority} priority, needs {task.duration_minutes} min "
                                  f"but only {remaining} min left.")
                )
        plan.scheduled = self.sort_by_time(plan.scheduled)
        return plan

"""CLI demo for PawPal+: builds an owner with two pets and exercises the Scheduler.

Run with:  python main.py
Output is plain ASCII so it prints cleanly in any terminal (including Windows).
"""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def print_header(title: str) -> None:
    """Print a section title underlined with '='."""
    print(f"\n{title}\n{'=' * len(title)}")


COLUMNS = [("DATE", 10), ("TIME", 11), ("PET", 5), ("TASK", 18), ("MIN", 3), ("PRIORITY", 8), ("REPEATS", 7), ("STATUS", 7)]


def print_tasks(tasks: list[Task], show_date: bool = False) -> None:
    """Print tasks as an aligned table (or a note when there are none)."""
    if not tasks:
        print("  (no tasks)")
        return
    columns = COLUMNS if show_date else COLUMNS[1:]

    def row(values: list[str]) -> str:
        return "  " + "  ".join(
            value.rjust(width) if name == "MIN" else value.ljust(width)
            for (name, width), value in zip(columns, values)
        ).rstrip()

    print(row([name for name, _ in columns]))
    print(row(["-" * width for _, width in columns]))
    for t in tasks:
        values = [
            f"{t.time}-{t.end_time}", t.pet_name, t.description, str(t.duration_minutes),
            t.priority, t.frequency, "done" if t.completed else "pending",
        ]
        print(row(([t.due_date.isoformat()] if show_date else []) + values))


def build_demo_owner(today: date) -> Owner:
    """Create Jordan with two pets and a day of tasks, added deliberately out of order."""
    owner = Owner(name="Jordan", available_minutes=150)
    mochi = owner.add_pet(Pet(name="Mochi", species="dog", age=3))
    luna = owner.add_pet(Pet(name="Luna", species="cat", age=5))

    mochi.add_task(Task("Evening walk", "18:30", 30, "medium", "daily", today))
    luna.add_task(Task("Play session", "17:00", 20, "medium", "daily", today))
    mochi.add_task(Task("Breakfast", "7:30", 10, "high", "daily", today))  # "7:30" is normalized to "07:30"
    mochi.add_task(Task("Vet checkup", "14:00", 60, "high", "once", today))
    luna.add_task(Task("Thyroid medication", "12:00", 5, "high", "daily", today))
    mochi.add_task(Task("Morning walk", "08:00", 30, "high", "daily", today))
    luna.add_task(Task("Brush coat", "08:00", 15, "low", "weekly", today))  # same time as the walk
    luna.add_task(Task("Breakfast", "07:45", 10, "high", "daily", today))
    mochi.add_task(Task("Grooming", "10:00", 45, "medium", "once", today + timedelta(days=1)))
    return owner


def main() -> None:
    """Run the PawPal+ terminal demo."""
    today = date.today()
    owner = build_demo_owner(today)
    scheduler = Scheduler(owner)

    print(f"PawPal+ | Owner: {owner.name} | Pets: {', '.join(p.name for p in owner.pets)} "
          f"| Daily care budget: {owner.available_minutes} min")

    print_header(f"Today's Schedule ({today:%a %Y-%m-%d}) - sorted by time")
    print_tasks(scheduler.todays_schedule(today))

    print_header("Sorted by priority (high first, ties by time)")
    print_tasks(scheduler.sort_by_priority(scheduler.get_tasks_for_date(today)))

    print_header("Filter: Mochi's tasks (all dates)")
    print_tasks(scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi")), show_date=True)

    print_header("Conflict check")
    conflicts = scheduler.find_conflicts(today)
    for message in scheduler.detect_conflicts(today):
        print(f"  WARNING: {message}")
    for first, second in conflicts:
        suggestion = scheduler.suggest_reschedule(first, second)
        if suggestion:
            task, slot = suggestion
            print(f"  Suggestion: move {task.pet_name}'s '{task.description}' to {slot} (next free slot).")
    if not conflicts:
        print("  No conflicts today.")

    print_header("Recurring tasks: completing Mochi's daily breakfast")
    breakfast = next(t for t in scheduler.filter_tasks(pet_name="Mochi") if t.description == "Breakfast")
    follow_up = scheduler.mark_task_complete(breakfast)
    print(f"  Marked '{breakfast.description}' ({breakfast.due_date}) complete -> completed={breakfast.completed}")
    if follow_up:
        print(f"  Auto-created next {follow_up.frequency} occurrence: "
              f"'{follow_up.description}' on {follow_up.due_date} at {follow_up.time}")

    print_header("Filter: pending tasks today")
    print_tasks(scheduler.sort_by_time(scheduler.filter_tasks(completed=False, tasks=scheduler.get_tasks_for_date(today))))

    print_header(f"Tomorrow's Schedule ({today + timedelta(days=1):%a %Y-%m-%d})")
    print_tasks(scheduler.todays_schedule(today + timedelta(days=1)))

    plan = scheduler.generate_daily_plan(today)
    print_header(f"Daily plan: {plan.minutes_used} of {plan.minutes_available} min used")
    print_tasks(plan.scheduled)
    print("\n  Why:")
    for line in plan.explain():
        print(f"   - {line}")


if __name__ == "__main__":
    main()

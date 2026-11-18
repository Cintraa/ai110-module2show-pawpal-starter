"""Automated tests for the PawPal+ logic layer (pawpal_system.py)."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

TODAY = date(2026, 11, 18)
TOMORROW = TODAY + timedelta(days=1)


@pytest.fixture
def owner() -> Owner:
    """An owner with two pets and no tasks yet."""
    jordan = Owner(name="Jordan", available_minutes=60)
    jordan.add_pet(Pet(name="Mochi", species="dog"))
    jordan.add_pet(Pet(name="Luna", species="cat"))
    return jordan


@pytest.fixture
def scheduler(owner: Owner) -> Scheduler:
    """A scheduler wired to the two-pet owner."""
    return Scheduler(owner)


def add(owner: Owner, pet: str, description: str, time: str, **kwargs) -> Task:
    """Helper: create a task due TODAY (unless overridden) and attach it to a pet."""
    kwargs.setdefault("due_date", TODAY)
    return owner.get_pet(pet).add_task(Task(description, time, **kwargs))


# --------------------------------------------------------------------------- #
# Phase 2 quick tests: Task completion and Task addition
# --------------------------------------------------------------------------- #
def test_mark_complete_changes_status():
    task = Task("Morning walk", "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Mochi")
    assert pet.task_count == 0
    pet.add_task(Task("Breakfast", "07:30"))
    pet.add_task(Task("Walk", "08:00"))
    assert pet.task_count == 2
    assert all(t.pet_name == "Mochi" for t in pet.tasks)


# --------------------------------------------------------------------------- #
# Task validation
# --------------------------------------------------------------------------- #
def test_time_is_normalized_to_zero_padded_hhmm():
    assert Task("Pill", "7:05").time == "07:05"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"time": "25:00"},
        {"time": "8am"},
        {"priority": "urgent"},
        {"frequency": "monthly"},
        {"duration_minutes": 0},
        {"description": "   "},
    ],
    ids=["hour-25", "am-pm-format", "unknown-priority", "unknown-frequency", "zero-duration", "blank-description"],
)
def test_invalid_task_fields_raise_value_error(kwargs):
    fields = {"description": "Walk", "time": "08:00", **kwargs}
    with pytest.raises(ValueError):
        Task(**fields)


# --------------------------------------------------------------------------- #
# Owner: multi-pet access
# --------------------------------------------------------------------------- #
def test_get_all_tasks_collects_tasks_from_every_pet(owner):
    add(owner, "Mochi", "Walk", "08:00")
    add(owner, "Luna", "Breakfast", "07:00")
    assert {t.pet_name for t in owner.get_all_tasks()} == {"Mochi", "Luna"}
    assert len(owner.get_all_tasks()) == 2


def test_duplicate_pet_names_are_rejected(owner):
    with pytest.raises(ValueError):
        owner.add_pet(Pet(name="mochi"))


def test_pet_with_no_tasks_produces_empty_results(scheduler):
    assert scheduler.todays_schedule(TODAY) == []
    assert scheduler.detect_conflicts(TODAY) == []
    plan = scheduler.generate_daily_plan(TODAY)
    assert plan.scheduled == [] and plan.skipped == []


# --------------------------------------------------------------------------- #
# Sorting
# --------------------------------------------------------------------------- #
def test_sort_by_time_returns_chronological_order(owner, scheduler):
    add(owner, "Mochi", "Evening walk", "18:30")
    add(owner, "Luna", "Breakfast", "07:45")
    add(owner, "Mochi", "Vet", "14:00")
    add(owner, "Luna", "Meds", "12:00")
    times = [t.time for t in scheduler.sort_by_time()]
    assert times == ["07:45", "12:00", "14:00", "18:30"]


def test_sort_by_time_handles_single_digit_hours(owner, scheduler):
    add(owner, "Mochi", "Late", "10:00")
    add(owner, "Mochi", "Early", "9:00")  # would sort after "10:00" as a raw string
    assert [t.description for t in scheduler.sort_by_time()] == ["Early", "Late"]


def test_sort_by_time_orders_by_date_first(owner, scheduler):
    add(owner, "Mochi", "Tomorrow early", "06:00", due_date=TOMORROW)
    add(owner, "Mochi", "Today late", "21:00")
    assert [t.description for t in scheduler.sort_by_time()] == ["Today late", "Tomorrow early"]


def test_sort_by_priority_puts_high_first_and_breaks_ties_by_time(owner, scheduler):
    add(owner, "Mochi", "Low", "07:00", priority="low")
    add(owner, "Luna", "High late", "12:00", priority="high")
    add(owner, "Mochi", "High early", "08:00", priority="high")
    add(owner, "Luna", "Medium", "06:00", priority="medium")
    order = [t.description for t in scheduler.sort_by_priority()]
    assert order == ["High early", "High late", "Medium", "Low"]


# --------------------------------------------------------------------------- #
# Filtering
# --------------------------------------------------------------------------- #
def test_filter_by_pet_name_is_case_insensitive(owner, scheduler):
    add(owner, "Mochi", "Walk", "08:00")
    add(owner, "Luna", "Brush", "09:00")
    assert [t.description for t in scheduler.filter_tasks(pet_name="mOcHi")] == ["Walk"]


def test_filter_by_completion_status(owner, scheduler):
    done = add(owner, "Mochi", "Walk", "08:00")
    add(owner, "Luna", "Brush", "09:00")
    done.mark_complete()
    assert [t.description for t in scheduler.filter_tasks(completed=True)] == ["Walk"]
    assert [t.description for t in scheduler.filter_tasks(completed=False)] == ["Brush"]


def test_filter_by_pet_and_status_combined(owner, scheduler):
    add(owner, "Mochi", "Walk", "08:00").mark_complete()
    add(owner, "Mochi", "Dinner", "18:00")
    add(owner, "Luna", "Brush", "09:00")
    result = scheduler.filter_tasks(pet_name="Mochi", completed=False)
    assert [t.description for t in result] == ["Dinner"]


def test_todays_schedule_excludes_other_dates(owner, scheduler):
    add(owner, "Mochi", "Today", "08:00")
    add(owner, "Mochi", "Tomorrow", "08:00", due_date=TOMORROW)
    assert [t.description for t in scheduler.todays_schedule(TODAY)] == ["Today"]


# --------------------------------------------------------------------------- #
# Recurring tasks
# --------------------------------------------------------------------------- #
def test_completing_daily_task_creates_task_for_next_day(owner, scheduler):
    walk = add(owner, "Mochi", "Walk", "08:00", frequency="daily")
    follow_up = scheduler.mark_task_complete(walk)

    assert walk.completed is True
    assert follow_up is not None
    assert follow_up.due_date == TODAY + timedelta(days=1)
    assert follow_up.completed is False
    assert (follow_up.description, follow_up.time, follow_up.pet_name) == ("Walk", "08:00", "Mochi")
    assert follow_up.task_id != walk.task_id
    assert follow_up in owner.get_pet("Mochi").tasks


def test_completing_weekly_task_creates_task_one_week_later(owner, scheduler):
    bath = add(owner, "Luna", "Bath", "10:00", frequency="weekly")
    follow_up = scheduler.mark_task_complete(bath)
    assert follow_up.due_date == TODAY + timedelta(weeks=1)


def test_completing_one_off_task_creates_nothing(owner, scheduler):
    vet = add(owner, "Mochi", "Vet", "14:00", frequency="once")
    assert scheduler.mark_task_complete(vet) is None
    assert owner.get_pet("Mochi").task_count == 1


def test_completing_same_task_twice_does_not_duplicate(owner, scheduler):
    walk = add(owner, "Mochi", "Walk", "08:00", frequency="daily")
    scheduler.mark_task_complete(walk)
    assert scheduler.mark_task_complete(walk) is None
    assert owner.get_pet("Mochi").task_count == 2  # original + one follow-up


# --------------------------------------------------------------------------- #
# Conflict detection
# --------------------------------------------------------------------------- #
def test_detects_duplicate_times_across_pets(owner, scheduler):
    add(owner, "Mochi", "Walk", "08:00", duration_minutes=30)
    add(owner, "Luna", "Brush", "08:00", duration_minutes=15)
    warnings = scheduler.detect_conflicts(TODAY)
    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Brush" in warnings[0]


def test_detects_overlapping_durations_for_same_pet(owner, scheduler):
    add(owner, "Mochi", "Walk", "08:00", duration_minutes=30)
    add(owner, "Mochi", "Training", "08:20", duration_minutes=15)
    warnings = scheduler.detect_conflicts(TODAY)
    assert len(warnings) == 1 and "same pet (Mochi)" in warnings[0]


def test_back_to_back_tasks_do_not_conflict(owner, scheduler):
    add(owner, "Mochi", "Walk", "08:00", duration_minutes=30)
    add(owner, "Mochi", "Breakfast", "08:30", duration_minutes=10)
    assert scheduler.detect_conflicts(TODAY) == []


def test_conflicts_ignore_completed_tasks_and_other_days(owner, scheduler):
    add(owner, "Mochi", "Walk", "08:00").mark_complete()
    add(owner, "Luna", "Brush", "08:00")
    add(owner, "Mochi", "Tomorrow walk", "08:00", due_date=TOMORROW)
    assert scheduler.detect_conflicts(TODAY) == []


def test_three_way_overlap_reports_every_pair(owner, scheduler):
    for pet, name in [("Mochi", "A"), ("Luna", "B"), ("Mochi", "C")]:
        add(owner, pet, name, "09:00", duration_minutes=20)
    assert len(scheduler.find_conflicts(TODAY)) == 3


def test_suggest_reschedule_moves_lower_priority_task_to_next_free_slot(owner, scheduler):
    walk = add(owner, "Mochi", "Walk", "08:00", duration_minutes=30, priority="high")
    brush = add(owner, "Luna", "Brush", "08:00", duration_minutes=15, priority="low")
    add(owner, "Mochi", "Breakfast", "08:30", duration_minutes=10)
    task, slot = scheduler.suggest_reschedule(walk, brush)
    assert task is brush and slot == "08:40"
    brush.reschedule(slot)
    assert scheduler.detect_conflicts(TODAY) == []


def test_find_next_free_slot_returns_none_when_day_is_full(owner, scheduler):
    add(owner, "Mochi", "All day", "06:00", duration_minutes=16 * 60)
    assert scheduler.find_next_free_slot(15, TODAY) is None


# --------------------------------------------------------------------------- #
# Daily plan (time budget + priority)
# --------------------------------------------------------------------------- #
def test_daily_plan_respects_time_budget_and_priority(owner, scheduler):
    # budget is 60 minutes (fixture)
    add(owner, "Mochi", "Walk", "08:00", duration_minutes=40, priority="high")
    add(owner, "Luna", "Play", "17:00", duration_minutes=30, priority="medium")
    add(owner, "Luna", "Meds", "12:00", duration_minutes=5, priority="high")
    plan = scheduler.generate_daily_plan(TODAY)

    assert [t.description for t in plan.scheduled] == ["Walk", "Meds"]  # chronological
    assert [t.description for t in plan.skipped] == ["Play"]
    assert plan.minutes_used == 45 <= plan.minutes_available
    assert len(plan.explain()) == 3

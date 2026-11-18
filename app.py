"""PawPal+ Streamlit UI.

This file is only the presentation layer: every action calls a method on the
classes in pawpal_system.py. The Owner object lives in st.session_state so it
survives Streamlit's top-to-bottom reruns.

Run with:  streamlit run app.py
"""

from datetime import date, time

import streamlit as st

from main import build_demo_owner
from pawpal_system import PRIORITY_RANK, VALID_FREQUENCIES, Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

PRIORITY_ICON = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}
SPECIES = ["dog", "cat", "rabbit", "bird", "other"]


# --------------------------------------------------------------------------- #
# Session "memory": create the Owner once, then reuse it on every rerun
# --------------------------------------------------------------------------- #
def sync_owner_widgets() -> None:
    """Copy the owner's settings into the sidebar widgets' session keys."""
    st.session_state.owner_name = st.session_state.owner.name
    st.session_state.owner_minutes = st.session_state.owner.available_minutes


if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)
    sync_owner_widgets()


def flash(kind: str, message: str) -> None:
    """Queue a message (success / warning / info / error) to show at the top of the next render."""
    st.session_state.setdefault("flash", []).append((kind, message))


def get_owner() -> Owner:
    """The Owner stored in the session."""
    return st.session_state.owner


# --------------------------------------------------------------------------- #
# Callbacks: they run before the script re-renders, so the page always shows fresh data
# --------------------------------------------------------------------------- #
def load_demo() -> None:
    """Replace the session's owner with the demo owner from main.py."""
    st.session_state.owner = build_demo_owner(date.today())
    sync_owner_widgets()
    flash("success", "Loaded demo data: Jordan with Mochi (dog) and Luna (cat).")


def reset_all() -> None:
    """Start over with an empty owner."""
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)
    st.session_state.pop("show_plan", None)
    sync_owner_widgets()
    flash("info", "Cleared all pets and tasks.")


def add_pet() -> None:
    """Form callback: create a Pet and hand it to Owner.add_pet."""
    ss = st.session_state
    try:
        pet = get_owner().add_pet(Pet(name=ss.new_pet_name, species=ss.new_pet_species, age=int(ss.new_pet_age)))
        flash("success", f"Added {pet.name} the {pet.species}.")
    except ValueError as err:
        flash("error", str(err))


def add_task() -> None:
    """Form callback: build a Task, attach it with Pet.add_task, then check for conflicts."""
    ss = st.session_state
    owner = get_owner()
    pet = owner.get_pet(ss.task_pet or "")
    if pet is None:
        flash("error", "Pick a pet first.")
        return
    try:
        task = Task(
            description=ss.task_description,
            time=ss.task_time.strftime("%H:%M"),
            duration_minutes=int(ss.task_duration),
            priority=ss.task_priority,
            frequency=ss.task_frequency,
            due_date=ss.task_date,
        )
    except ValueError as err:
        flash("error", str(err))
        return
    pet.add_task(task)
    scheduler = Scheduler(owner)
    clashes = [pair for pair in scheduler.find_conflicts(task.due_date) if task in pair]
    if clashes:
        other = clashes[0][0] if clashes[0][1] is task else clashes[0][1]
        flash("warning", f"Added '{task.description}' for {pet.name} at {task.time}, but it overlaps "
                         f"{other.pet_name}'s '{other.description}' ({other.time}-{other.end_time}). "
                         "See the conflict panel below for a suggested fix.")
    else:
        flash("success", f"Scheduled '{task.description}' for {pet.name} on {task.due_date:%a %b %d} at {task.time}.")


def complete_task(task_id: str) -> None:
    """Mark a task complete through the Scheduler so recurring tasks roll forward."""
    owner = get_owner()
    task = owner.find_task(task_id)
    if task is None:
        return
    follow_up = Scheduler(owner).mark_task_complete(task)
    message = f"Completed {task.pet_name}'s '{task.description}'."
    if follow_up:
        message += f" Next {follow_up.frequency} occurrence added for {follow_up.due_date:%a %b %d} at {follow_up.time}."
    flash("success", message)


def remove_task(task_id: str) -> None:
    """Delete a task from its pet."""
    owner = get_owner()
    task = owner.find_task(task_id)
    if task and owner.get_pet(task.pet_name).remove_task(task_id):
        flash("info", f"Removed {task.pet_name}'s '{task.description}'.")


def apply_reschedule(task_id: str, new_time: str) -> None:
    """Accept a conflict fix: move the task to the suggested time."""
    task = get_owner().find_task(task_id)
    if task:
        task.reschedule(new_time)
        flash("success", f"Moved {task.pet_name}'s '{task.description}' to {new_time}.")


# --------------------------------------------------------------------------- #
# Display helpers
# --------------------------------------------------------------------------- #
def task_rows(tasks: list[Task]) -> list[dict]:
    """Turn Task objects into table rows."""
    return [
        {
            "Time": f"{t.time}–{t.end_time}",
            "Pet": t.pet_name,
            "Task": t.description,
            "Minutes": t.duration_minutes,
            "Priority": PRIORITY_ICON[t.priority],
            "Repeats": t.frequency,
            "Status": "✅ done" if t.completed else "⏳ pending",
        }
        for t in tasks
    ]


# --------------------------------------------------------------------------- #
# Sidebar: owner settings
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.header("👤 Owner")
    st.text_input("Owner name", key="owner_name")
    st.number_input("Minutes available for pet care per day", min_value=10, max_value=720, step=10,
                    key="owner_minutes")
    st.divider()
    st.button("Load demo data", on_click=load_demo)
    st.button("Reset everything", on_click=reset_all)
    st.caption("Demo data = the same owner and pets that `python main.py` prints.")

owner = get_owner()
owner.name = st.session_state.owner_name.strip() or owner.name
owner.available_minutes = int(st.session_state.owner_minutes)
scheduler = Scheduler(owner)

# --------------------------------------------------------------------------- #
# Header
# --------------------------------------------------------------------------- #
st.title("🐾 PawPal+")
st.caption(f"Smart pet care planner for **{owner.name}** — sorting, filtering, recurring tasks and conflict warnings.")

for kind, message in st.session_state.pop("flash", []):
    getattr(st, kind)(message)

today_tasks = scheduler.get_tasks_for_date(date.today())
m1, m2, m3, m4 = st.columns(4)
m1.metric("Pets", len(owner.pets))
m2.metric("Tasks today", len(today_tasks))
m3.metric("Pending today", len([t for t in today_tasks if not t.completed]))
m4.metric("Conflicts today", len(scheduler.find_conflicts(date.today())))

# --------------------------------------------------------------------------- #
# Add pets and tasks
# --------------------------------------------------------------------------- #
left, right = st.columns(2)

with left:
    st.subheader("➕ Add a pet")
    with st.form("add_pet_form", clear_on_submit=True):
        st.text_input("Pet name", key="new_pet_name", placeholder="e.g. Mochi")
        c1, c2 = st.columns(2)
        c1.selectbox("Species", SPECIES, key="new_pet_species")
        c2.number_input("Age (years)", min_value=0, max_value=40, value=1, key="new_pet_age")
        st.form_submit_button("Add pet", on_click=add_pet)

    st.subheader("🐶 Your pets")
    if owner.pets:
        st.dataframe(
            [
                {"Pet": p.name, "Species": p.species, "Age": p.age, "Tasks": p.task_count,
                 "Pending": len(p.get_tasks(include_completed=False))}
                for p in owner.pets
            ],
            hide_index=True,
        )
    else:
        st.info("No pets yet — add one above or click **Load demo data** in the sidebar.")

with right:
    st.subheader("🗓️ Schedule a task")
    if not owner.pets:
        st.info("Add a pet first, then you can schedule its tasks here.")
    else:
        with st.form("add_task_form", clear_on_submit=True):
            st.selectbox("Pet", [p.name for p in owner.pets], key="task_pet")
            st.text_input("Task", key="task_description", placeholder="e.g. Morning walk")
            c1, c2 = st.columns(2)
            c1.time_input("Start time", value=time(8, 0), step=300, key="task_time")
            c2.number_input("Duration (minutes)", min_value=1, max_value=480, value=20, key="task_duration")
            c3, c4, c5 = st.columns(3)
            c3.selectbox("Priority", list(PRIORITY_RANK), index=1, key="task_priority")
            c4.selectbox("Repeats", list(VALID_FREQUENCIES), key="task_frequency")
            c5.date_input("Date", value=date.today(), key="task_date")
            st.form_submit_button("Add task", on_click=add_task, type="primary")

st.divider()

# --------------------------------------------------------------------------- #
# Schedule view: Scheduler sorting + filtering + conflicts
# --------------------------------------------------------------------------- #
st.subheader("📅 Schedule")
f1, f2, f3, f4 = st.columns([1.2, 1.2, 1.4, 1.2])
view_day = f1.date_input("Day", value=date.today(), key="view_day")
pet_filter = f2.selectbox("Pet", ["All pets"] + [p.name for p in owner.pets], key="view_pet")
status_filter = f3.radio("Status", ["All", "Pending", "Completed"], horizontal=True, key="view_status")
sort_mode = f4.radio("Sort by", ["Time", "Priority"], horizontal=True, key="view_sort")

day_tasks = scheduler.get_tasks_for_date(view_day)
filtered = scheduler.filter_tasks(
    pet_name=None if pet_filter == "All pets" else pet_filter,
    completed={"All": None, "Pending": False, "Completed": True}[status_filter],
    tasks=day_tasks,
)
ordered = scheduler.sort_by_time(filtered) if sort_mode == "Time" else scheduler.sort_by_priority(filtered)

# Conflict warnings go right above the table, each with a one-click fix.
conflicts = scheduler.find_conflicts(view_day)
for (first, second), message in zip(conflicts, scheduler.detect_conflicts(view_day)):
    warn_col, fix_col = st.columns([3, 1])
    warn_col.warning(f"⚠️ {message}")
    suggestion = scheduler.suggest_reschedule(first, second)
    if suggestion:
        task, slot = suggestion
        fix_col.button(f"Move {task.pet_name}'s {task.description} to {slot}",
                       key=f"fix-{first.task_id}-{second.task_id}",
                       on_click=apply_reschedule, args=(task.task_id, slot))
    else:
        fix_col.caption("No free slot left today — consider another day.")
if day_tasks and not conflicts:
    st.success(f"No time conflicts on {view_day:%a %b %d}.")

if ordered:
    st.dataframe(task_rows(ordered), hide_index=True)
elif day_tasks:
    st.info("No tasks match these filters.")
else:
    st.info(f"Nothing scheduled for {view_day:%a %b %d}.")

pending = scheduler.sort_by_time(scheduler.filter_tasks(completed=False, tasks=day_tasks))
if pending:
    a1, a2, a3 = st.columns([3, 1, 1])
    choice = a1.selectbox(
        "Pick a pending task",
        [t.task_id for t in pending],
        format_func=lambda tid: owner.find_task(tid).summary(),
        key="action_task",
    )
    a2.button("✅ Mark complete", on_click=complete_task, args=(choice,))
    a3.button("🗑️ Remove", on_click=remove_task, args=(choice,))

st.divider()

# --------------------------------------------------------------------------- #
# Daily plan: priority + time budget, with reasoning
# --------------------------------------------------------------------------- #
st.subheader("🧠 Daily plan")
st.caption(f"Fits the most important pending tasks into {owner.name}'s {owner.available_minutes}-minute budget, "
           "high priority first, then shows them in time order.")
if st.button("Generate plan for selected day", type="primary"):
    st.session_state.show_plan = True

if st.session_state.get("show_plan"):
    plan = scheduler.generate_daily_plan(view_day)
    if not plan.decisions:
        st.info(f"No pending tasks on {view_day:%a %b %d} to plan.")
    else:
        st.progress(min(plan.minutes_used / plan.minutes_available, 1.0),
                    text=f"{plan.minutes_used} of {plan.minutes_available} minutes used")
        if plan.scheduled:
            st.table(task_rows(plan.scheduled))
        if plan.skipped:
            st.warning("Didn't fit today: " + ", ".join(f"{t.pet_name}'s {t.description}" for t in plan.skipped)
                       + ". Raise your time budget in the sidebar or lower other priorities.")
        with st.expander("Why this plan?", expanded=True):
            for line in plan.explain():
                st.markdown(f"- {line}")

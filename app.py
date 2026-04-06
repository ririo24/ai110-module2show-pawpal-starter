import streamlit as st
from datetime import date
import uuid
import pandas as pd
from pawpal_system import Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Persist Owner in session_state; load from data.json on first run ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner.load_from_json()

owner: Owner = st.session_state.owner

# ── Display helpers ────────────────────────────────────────────────────────────

SPECIES_EMOJI  = {"dog": "🐕", "cat": "🐈", "other": "🐾"}
TYPE_ICON      = {"walk": "🦮", "feeding": "🍖", "vet": "🏥", "grooming": "✂️"}
STATUS_BADGE   = {"pending": "🟡 Pending", "completed": "✅ Completed", "cancelled": "❌ Cancelled"}
PRIORITY_BADGE = {"High": "🔴 High", "Medium": "🟡 Medium", "Low": "🟢 Low"}

PRIORITY_BG = {"🔴 High": "#ffe5e5", "🟡 Medium": "#fffde7", "🟢 Low": "#e8f5e9"}
STATUS_BG   = {"🟡 Pending": "#fffde7", "✅ Completed": "#e8f5e9", "❌ Cancelled": "#f5f5f5"}


def _row_color_by_priority(row):
    bg = PRIORITY_BG.get(str(row.get("Priority", "")), "#ffffff")
    return [f"background-color: {bg}; color: #222"] * len(row)


def _row_color_by_status(row):
    bg = STATUS_BG.get(str(row.get("Status", "")), "#ffffff")
    return [f"background-color: {bg}; color: #222"] * len(row)


# ── SECTION 1: Owner Profile ───────────────────────────────────────────────────

st.subheader("👤 Owner Profile")

with st.form("owner_form"):
    owner_name  = st.text_input("Your name",  value=owner.name)
    owner_email = st.text_input("Email",       value=owner.email)
    owner_phone = st.text_input("Phone",       value=owner.phone)
    if st.form_submit_button("💾 Save profile"):
        owner.name  = owner_name
        owner.email = owner_email
        owner.phone = owner_phone
        owner.save_to_json()
        st.success(f"Profile saved for **{owner.name}**!")

st.divider()

# ── SECTION 2: Pets ────────────────────────────────────────────────────────────

st.subheader("🐾 Your Pets")

with st.form("add_pet_form"):
    pet_name    = st.text_input("Pet name",  value="Mochi")
    pet_species = st.selectbox("Species",    ["dog", "cat", "other"])
    pet_breed   = st.text_input("Breed",     value="Mixed")
    pet_age     = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
    pet_weight  = st.number_input("Weight (kg)",  min_value=0.1, max_value=200.0, value=5.0)

    if st.form_submit_button("➕ Add pet"):
        new_pet = Pet(
            id=str(uuid.uuid4()),
            name=pet_name,
            species=pet_species,
            breed=pet_breed,
            age=int(pet_age),
            weight=float(pet_weight),
            owner_id=owner.id,
        )
        owner.add_pet(new_pet)
        owner.save_to_json()
        st.success(f"{SPECIES_EMOJI.get(pet_species, '🐾')} **{new_pet.name}** added!")

if owner.pets:
    pet_df = pd.DataFrame([
        {
            "":            SPECIES_EMOJI.get(p.species, "🐾"),
            "Name":        p.name,
            "Species":     p.species.capitalize(),
            "Breed":       p.breed,
            "Age (yrs)":   p.age,
            "Weight (kg)": p.weight,
        }
        for p in owner.pets
    ])
    st.dataframe(pet_df, hide_index=True, use_container_width=True)
else:
    st.info("No pets yet — add one above.")

st.divider()

# ── SECTION 3: Schedule a Task ─────────────────────────────────────────────────

st.subheader("📅 Schedule a Task")

if not owner.pets:
    st.warning("Add a pet first before scheduling a task.")
else:
    with st.form("add_task_form"):
        pet_options       = {p.name: p for p in owner.pets}
        selected_pet_name = st.selectbox("Select pet", list(pet_options.keys()))
        task_title        = st.text_input("Task title", value="Morning walk")
        task_type         = st.selectbox("Task type", ["walk", "feeding", "vet", "grooming"])
        task_desc         = st.text_input("Notes", value="")
        task_date         = st.date_input("Due date", value=date.today())
        task_time         = st.text_input("Time (HH:MM)", value="09:00")
        task_recur        = st.selectbox("Repeat", ["none", "daily", "weekly"])
        task_priority     = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)

        if st.form_submit_button("📌 Schedule task"):
            selected_pet = pet_options[selected_pet_name]
            new_task = Task(
                id=str(uuid.uuid4()),
                title=task_title,
                task_type=task_type,
                status="pending",
                due_date=task_date,
                pet=selected_pet,
                description=task_desc,
                time=task_time,
                recurrence=None if task_recur == "none" else task_recur,
                priority=task_priority,
            )
            warning = owner.scheduler.schedule_task(new_task)
            owner.save_to_json()
            st.success(
                f"{TYPE_ICON.get(task_type, '')} **{new_task.title}** scheduled for "
                f"**{selected_pet.name}** on {task_date} at {task_time} "
                f"— {PRIORITY_BADGE.get(task_priority, task_priority)}"
            )
            if warning:
                st.warning(
                    "⚠️ **Time conflict detected.**  \n"
                    f"**{new_task.title}** overlaps with another pending task.  \n"
                    "Check the **Scheduling Conflicts** section below."
                )

st.divider()

# ── SECTION 4: Today's Schedule ───────────────────────────────────────────────

st.subheader("🗓️ Today's Schedule")

todays_tasks = [t for t in owner.scheduler.sort_by_time() if t.due_date == date.today()]

if todays_tasks:
    # Quick-stat pills
    n_pending   = sum(1 for t in todays_tasks if t.status == "pending")
    n_completed = sum(1 for t in todays_tasks if t.status == "completed")
    n_high      = sum(1 for t in todays_tasks if t.priority == "High" and t.status == "pending")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total today",      len(todays_tasks))
    c2.metric("🟡 Pending",       n_pending)
    c3.metric("🔴 High priority", n_high)

    st.caption("Rows are color-coded: 🔴 red = High · 🟡 yellow = Medium · 🟢 green = Low")

    task_df = pd.DataFrame([
        {
            "Priority": PRIORITY_BADGE.get(t.priority, t.priority),
            "Time":     t.time,
            "Task":     f"{TYPE_ICON.get(t.task_type, '')} {t.title}",
            "Pet":      t.pet.name,
            "Type":     t.task_type.capitalize(),
            "Status":   STATUS_BADGE.get(t.status, t.status),
            "Notes":    t.description or "—",
        }
        for t in todays_tasks
    ])

    styled = task_df.style.apply(_row_color_by_priority, axis=1)
    st.dataframe(styled, hide_index=True, use_container_width=True)
else:
    st.info("No tasks scheduled for today.")

st.divider()

# ── SECTION 5: All Tasks ───────────────────────────────────────────────────────

st.subheader("📋 All Tasks")

all_tasks = owner.scheduler.sort_by_time()

if all_tasks:
    all_df = pd.DataFrame([
        {
            "Priority": PRIORITY_BADGE.get(t.priority, t.priority),
            "Date":     str(t.due_date),
            "Time":     t.time,
            "Task":     f"{TYPE_ICON.get(t.task_type, '')} {t.title}",
            "Pet":      t.pet.name,
            "Type":     t.task_type.capitalize(),
            "Status":   STATUS_BADGE.get(t.status, t.status),
            "Repeat":   t.recurrence or "—",
            "Notes":    t.description or "—",
        }
        for t in all_tasks
    ])

    styled_all = all_df.style.apply(_row_color_by_status, axis=1)
    st.dataframe(styled_all, hide_index=True, use_container_width=True)
else:
    st.info("No tasks scheduled yet.")

st.divider()

# ── SECTION 6: Conflict Warnings ──────────────────────────────────────────────

st.subheader("⚠️ Scheduling Conflicts")

conflicts = owner.scheduler.get_conflicts()

if conflicts:
    st.warning(
        f"**{len(conflicts)} conflict{'s' if len(conflicts) != 1 else ''} found.**  \n"
        "These tasks overlap in time — reschedule one to avoid missed care."
    )
    conflict_df = pd.DataFrame([
        {
            "Date":        str(a.due_date),
            "Time":        a.time,
            "Task A":      f"{TYPE_ICON.get(a.task_type, '')} {a.title}",
            "Pet A":       a.pet.name,
            "Priority A":  PRIORITY_BADGE.get(a.priority, a.priority),
            "Task B":      f"{TYPE_ICON.get(b.task_type, '')} {b.title}",
            "Pet B":       b.pet.name,
            "Priority B":  PRIORITY_BADGE.get(b.priority, b.priority),
        }
        for a, b in conflicts
    ])
    st.dataframe(
        conflict_df.style.set_properties(**{"background-color": "#fff3cd", "color": "#222"}),
        hide_index=True,
        use_container_width=True,
    )
else:
    st.success("✅ No conflicts — your schedule is clear!")

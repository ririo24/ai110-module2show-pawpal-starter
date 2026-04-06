from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Create Owner ---
owner = Owner(id="o1", name="Alex Rivera", email="alex@email.com", phone="555-0100")

# --- Create Pets ---
buddy = Pet(id="p1", name="Buddy", species="Dog", breed="Labrador", age=3, weight=30.5, owner_id="o1")
whiskers = Pet(id="p2", name="Whiskers", species="Cat", breed="Tabby", age=5, weight=4.2, owner_id="o1")

owner.pets.append(buddy)
owner.pets.append(whiskers)

# --- Create Tasks (added out of order by time) ---
evening_walk = Task(
    id="t1",
    title="Evening Walk",
    task_type="walk",
    status="pending",
    due_date=date.today(),
    pet=buddy,
    description="30 min walk around the park",
    time="18:00"
)

breakfast = Task(
    id="t2",
    title="Breakfast Feeding",
    task_type="feeding",
    status="completed",
    due_date=date.today(),
    pet=whiskers,
    description="Half cup of dry food",
    time="07:30"
)

vet_checkup = Task(
    id="t3",
    title="Annual Vet Checkup",
    task_type="vet",
    status="pending",
    due_date=date.today(),
    pet=buddy,
    description="Yearly vaccinations and health check",
    time="14:00"
)

lunch_feeding = Task(
    id="t4",
    title="Lunch Feeding",
    task_type="feeding",
    status="pending",
    due_date=date.today(),
    pet=whiskers,
    description="Small treat and water refresh",
    time="12:00"
)

morning_walk = Task(
    id="t5",
    title="Morning Walk",
    task_type="walk",
    status="pending",
    due_date=date.today(),
    pet=buddy,
    description="Quick neighbourhood loop",
    time="08:15"
)

# --- Add tasks out of order ---
owner.scheduler.schedule_task(evening_walk)   # 18:00
owner.scheduler.schedule_task(breakfast)       # 07:30
owner.scheduler.schedule_task(vet_checkup)     # 14:00
owner.scheduler.schedule_task(lunch_feeding)   # 12:00
owner.scheduler.schedule_task(morning_walk)    # 08:15

# --- Helper to print a task list ---
def print_tasks(tasks: list[Task]) -> None:
    if not tasks:
        print("  (no tasks)\n")
        return
    for task in tasks:
        print(f"  [{task.time}]  [{task.status.upper()}]  {task.title}  —  {task.pet.name}")
    print()

# --- Sort by time ---
print("=" * 45)
print("  SORTED BY TIME (earliest → latest)")
print("=" * 45)
print_tasks(owner.scheduler.sort_by_time())

# --- Filter: pending only ---
print("=" * 45)
print("  FILTER: pending tasks")
print("=" * 45)
print_tasks(owner.scheduler.filter_tasks(status="pending"))

# --- Filter: completed only ---
print("=" * 45)
print("  FILTER: completed tasks")
print("=" * 45)
print_tasks(owner.scheduler.filter_tasks(status="completed"))

# --- Filter: tasks for Buddy ---
print("=" * 45)
print("  FILTER: tasks for Buddy")
print("=" * 45)
print_tasks(owner.scheduler.filter_tasks(pet_name="Buddy"))

# --- Filter: tasks for Whiskers ---
print("=" * 45)
print("  FILTER: tasks for Whiskers")
print("=" * 45)
print_tasks(owner.scheduler.filter_tasks(pet_name="Whiskers"))

# --- Combined filter: pending tasks for Buddy ---
print("=" * 45)
print("  FILTER: pending tasks for Buddy (combined)")
print("=" * 45)
print_tasks(owner.scheduler.filter_tasks(status="pending", pet_name="Buddy"))

# --- Recurring task demo ---
daily_feeding = Task(
    id="t6",
    title="Daily Feeding",
    task_type="feeding",
    status="pending",
    due_date=date.today(),
    pet=whiskers,
    description="Morning kibble",
    time="07:00",
    recurrence="daily"
)

weekly_grooming = Task(
    id="t7",
    title="Weekly Grooming",
    task_type="grooming",
    status="pending",
    due_date=date.today(),
    pet=buddy,
    description="Brush and bath",
    time="10:00",
    recurrence="weekly"
)

owner.scheduler.schedule_task(daily_feeding)
owner.scheduler.schedule_task(weekly_grooming)

print("=" * 45)
print("  RECURRING: before completing tasks")
print("=" * 45)
print_tasks(owner.scheduler.filter_tasks(pet_name="Whiskers"))
print_tasks(owner.scheduler.filter_tasks(pet_name="Buddy"))

next_feeding   = owner.scheduler.complete_task("t6")
next_grooming  = owner.scheduler.complete_task("t7")

print("=" * 45)
print("  RECURRING: after completing — new tasks auto-created")
print("=" * 45)
print(f"  Daily feeding  next due : {next_feeding.due_date}   (id: {next_feeding.id[:8]}...)")
print(f"  Weekly grooming next due: {next_grooming.due_date}  (id: {next_grooming.id[:8]}...)")
print()
print("  Full schedule after recurrence:")
print_tasks(owner.scheduler.sort_by_time())

# --- Conflict detection demo ---
# Two tasks intentionally set to the same date and time (14:00)
# to verify the Scheduler detects and reports the overlap.

grooming_conflict = Task(
    id="t8",
    title="Grooming Appointment",
    task_type="grooming",
    status="pending",
    due_date=date.today(),
    pet=whiskers,
    description="Nail trim and brush — same slot as Vet Checkup",
    time="14:00"
)

print("=" * 45)
print("  CONFLICT DETECTION: schedule_task() warning")
print("=" * 45)
print(f"  Scheduling '{grooming_conflict.title}' for {grooming_conflict.pet.name} at {grooming_conflict.time}...")
warning = owner.scheduler.schedule_task(grooming_conflict)
if warning:
    print(f"  {warning}")
else:
    print("  No conflict detected.")
print()

print("=" * 45)
print("  CONFLICT DETECTION: get_conflicts() scan")
print("=" * 45)
conflicts = owner.scheduler.get_conflicts()
if not conflicts:
    print("  No conflicts found.\n")
else:
    for a, b in conflicts:
        print(f"  [{a.time}]  '{a.title}' ({a.pet.name})  ><  '{b.title}' ({b.pet.name})  —  {a.due_date}")
    print()

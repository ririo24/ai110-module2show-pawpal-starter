from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Create Owner ---
owner = Owner(id="o1", name="Alex Rivera", email="alex@email.com", phone="555-0100")

# --- Create Pets ---
buddy = Pet(id="p1", name="Buddy", species="Dog", breed="Labrador", age=3, weight=30.5, owner_id="o1")
whiskers = Pet(id="p2", name="Whiskers", species="Cat", breed="Tabby", age=5, weight=4.2, owner_id="o1")

owner.pets.append(buddy)
owner.pets.append(whiskers)

# --- Create Tasks ---
morning_walk = Task(
    id="t1",
    title="Morning Walk",
    task_type="walk",
    status="pending",
    due_date=date.today(),
    pet=buddy,
    description="30 min walk around the park"
)

breakfast = Task(
    id="t2",
    title="Breakfast Feeding",
    task_type="feeding",
    status="pending",
    due_date=date.today(),
    pet=whiskers,
    description="Half cup of dry food"
)

vet_checkup = Task(
    id="t3",
    title="Annual Vet Checkup",
    task_type="vet",
    status="pending",
    due_date=date.today(),
    pet=buddy,
    description="Yearly vaccinations and health check"
)

# --- Add Tasks to Scheduler ---
owner.scheduler.tasks.append(morning_walk)
owner.scheduler.tasks.append(breakfast)
owner.scheduler.tasks.append(vet_checkup)

# --- Print Today's Schedule ---
print("=" * 40)
print(f"  PawPal+ | Today's Schedule")
print(f"  Owner: {owner.name}  |  Date: {date.today()}")
print("=" * 40)

for task in owner.scheduler.tasks:
    print(f"\n[{task.status.upper()}]  {task.title}")
    print(f"  Pet      : {task.pet.name} ({task.pet.species})")
    print(f"  Type     : {task.task_type}")
    print(f"  Notes    : {task.description}")

print("\n" + "=" * 40)

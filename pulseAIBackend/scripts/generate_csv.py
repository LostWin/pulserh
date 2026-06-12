import os
import csv
import random
from datetime import datetime, timedelta
from faker import Faker

# Use multiple locales to mix names
fake = Faker(['ar_AA', 'fr_FR', 'en_US'])

# Ensure the output directory exists
os.makedirs("data_imports", exist_ok=True)

# Helper for date string
def get_random_date(start_years_ago=5, end_years_ago=0):
    start = datetime.now() - timedelta(days=365 * start_years_ago)
    end = datetime.now() - timedelta(days=365 * end_years_ago)
    return fake.date_between(start_date=start, end_date=end).isoformat()

# Number of entities
NUM_EMPLOYEES = 500

print("Generating Data...")

# ---------------------------------------------------------
# 1. Departments & Jobs Definitions
# ---------------------------------------------------------
print("Generating 01_departments.csv & 02_jobs.csv")

departments_data = {
    "dep-1": {
        "name": "Ressources Humaines",
        "jobs": [
            {"title": "Directeur RH", "level": "Executive"},
            {"title": "HR Business Partner", "level": "Senior"},
            {"title": "Chargé de Recrutement", "level": "Mid"},
            {"title": "Gestionnaire de Paie", "level": "Mid"},
            {"title": "Office Manager", "level": "Junior"}
        ]
    },
    "dep-2": {
        "name": "IT & Engineering",
        "jobs": [
            {"title": "Directeur Technique", "level": "Executive"},
            {"title": "Lead Développeur", "level": "Senior"},
            {"title": "Développeur Backend", "level": "Mid"},
            {"title": "Développeur Frontend", "level": "Mid"},
            {"title": "Ingénieur DevOps", "level": "Senior"},
            {"title": "QA Tester", "level": "Junior"},
            {"title": "Data Scientist", "level": "Mid"}
        ]
    },
    "dep-3": {
        "name": "Finance & Comptabilité",
        "jobs": [
            {"title": "Directeur Financier", "level": "Executive"},
            {"title": "Contrôleur de Gestion", "level": "Senior"},
            {"title": "Comptable", "level": "Mid"},
            {"title": "Analyste Financier", "level": "Junior"}
        ]
    },
    "dep-4": {
        "name": "Marketing & Communication",
        "jobs": [
            {"title": "Directeur Marketing", "level": "Executive"},
            {"title": "Product Marketing Manager", "level": "Senior"},
            {"title": "Community Manager", "level": "Junior"},
            {"title": "Content Creator", "level": "Mid"},
            {"title": "SEO Specialist", "level": "Mid"}
        ]
    },
    "dep-5": {
        "name": "Ventes",
        "jobs": [
            {"title": "Directeur Commercial", "level": "Executive"},
            {"title": "Key Account Manager", "level": "Senior"},
            {"title": "Commercial B2B", "level": "Mid"},
            {"title": "SDR", "level": "Junior"}
        ]
    },
    "dep-6": {
        "name": "Direction Générale",
        "jobs": [
            {"title": "Directeur Général", "level": "Executive"},
            {"title": "COO", "level": "Executive"},
            {"title": "Assistant de Direction", "level": "Mid"}
        ]
    }
}

departments = []
jobs = []
dep_to_jobs = {} # mapping dep_id -> list of job_ids
job_id_counter = 1

for dep_id, dep_info in departments_data.items():
    departments.append({"id": dep_id, "name": dep_info["name"], "manager_id": ""})
    dep_to_jobs[dep_id] = []
    
    for job_info in dep_info["jobs"]:
        j_id = f"job-{job_id_counter}"
        job_id_counter += 1
        jobs.append({
            "id": j_id,
            "title": job_info["title"],
            "level": job_info["level"],
            "description": f"Poste de {job_info['title']} au sein du département {dep_info['name']}."
        })
        dep_to_jobs[dep_id].append(j_id)

with open("data_imports/01_departments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "manager_id"])
    writer.writeheader()
    for d in departments:
        writer.writerow(d)

with open("data_imports/02_jobs.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "title", "level", "description"])
    writer.writeheader()
    for j in jobs:
        writer.writerow(j)

# ---------------------------------------------------------
# 3. Employees
# ---------------------------------------------------------
print("Generating 03_employees.csv")
employees = []
managers_pool = []
dep_ids = list(dep_to_jobs.keys())

for i in range(1, NUM_EMPLOYEES + 1):
    emp_id = f"emp-{i}"
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    # Create email
    import re
    import uuid
    base_email = f"{first_name}.{last_name}".lower()
    clean_prefix = re.sub(r"[^a-z0-9]", "", base_email.replace(".", ""))
    if not clean_prefix:
        clean_prefix = "user"
    email_clean = f"{clean_prefix}.{str(uuid.uuid4())[:6]}@pulse.com"
    
    # Assign manager (first 20 are directors/managers with no manager)
    manager_id = ""
    if i > 20:
        manager_id = random.choice(managers_pool)
    else:
        managers_pool.append(emp_id)
        
    dep_id = random.choice(dep_ids)
    job_id = random.choice(dep_to_jobs[dep_id]) # Select a job specific to this department
        
    employees.append({
        "id": emp_id,
        "user_id": fake.uuid4() if random.random() > 0.5 else "", # 50% linked to keycloak roughly
        "first_name": first_name,
        "last_name": last_name,
        "email": email_clean,
        "phone": fake.phone_number(),
        "hire_date": get_random_date(10, 0),
        "status": random.choices(["actif", "inactif", "suspendu"], weights=[85, 10, 5])[0],
        "department_id": dep_id,
        "job_id": job_id,
        "manager_id": manager_id
    })

with open("data_imports/03_employees.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "user_id", "first_name", "last_name", "email", "phone", "hire_date", "status", "department_id", "job_id", "manager_id"])
    writer.writeheader()
    for e in employees:
        writer.writerow(e)

# Update department managers now that we have employees
for d in departments:
    # Pick a random employee in this department as manager
    dept_employees = [e for e in employees if e["department_id"] == d["id"]]
    if dept_employees:
        d["manager_id"] = random.choice(dept_employees)["id"]

with open("data_imports/01_departments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "manager_id"])
    writer.writeheader()
    for d in departments:
        writer.writerow(d)

# ---------------------------------------------------------
# 4. Contracts
# ---------------------------------------------------------
print("Generating 04_contracts.csv")
contracts = []
for i, emp in enumerate(employees):
    # Some employees might have a previous contract and a current one
    has_history = random.random() > 0.7
    
    hire_date = datetime.fromisoformat(emp["hire_date"])
    
    if has_history:
        # Prev contract (e.g., CDD)
        cdd_duration = timedelta(days=random.randint(180, 365))
        cdd_end = hire_date + cdd_duration
        contracts.append({
            "id": fake.uuid4(),
            "employee_id": emp["id"],
            "contract_type": "CDD",
            "start_date": hire_date.isoformat(),
            "end_date": cdd_end.isoformat(),
            "salary": random.randint(30000, 45000),
            "is_active": "false"
        })
        current_start = cdd_end + timedelta(days=1)
    else:
        current_start = hire_date

    # Current contract
    is_active = emp["status"] == "actif"
    contracts.append({
        "id": fake.uuid4(),
        "employee_id": emp["id"],
        "contract_type": "CDI",
        "start_date": current_start.isoformat(),
        "end_date": "",
        "salary": random.randint(40000, 90000),
        "is_active": str(is_active).lower()
    })

with open("data_imports/04_contracts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "contract_type", "start_date", "end_date", "salary", "is_active"])
    writer.writeheader()
    for c in contracts:
        writer.writerow(c)

# ---------------------------------------------------------
# 5. Leaves (Congés)
# ---------------------------------------------------------
print("Generating 05_leaves.csv")
leave_types = ["Congés Payés", "Maladie", "Maternité/Paternité", "Autres", "Raisons personnelles"]
leaves = []
for emp in employees:
    if random.random() > 0.2: # 80% took leaves
        num_leaves = random.randint(1, 4)
        for _ in range(num_leaves):
            start = fake.date_between(start_date="-1y", end_date="+3m")
            duration = timedelta(days=random.randint(1, 14))
            end = start + duration
            leaves.append({
                "id": fake.uuid4(),
                "employee_id": emp["id"],
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "leave_type": random.choice(leave_types),
                "status": random.choices(["Approuvé", "En attente", "Rejeté"], weights=[80, 15, 5])[0],
                "reason": "Généré automatiquement"
            })

with open("data_imports/05_leaves.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "start_date", "end_date", "leave_type", "status", "reason"])
    writer.writeheader()
    for l in leaves:
        writer.writerow(l)

# ---------------------------------------------------------
# 6. Projects & Tasks
# ---------------------------------------------------------
print("Generating 06_projects_and_tasks.csv")
projects = []
tasks = []

for i in range(1, 11):
    proj_id = f"proj-{i}"
    start = fake.date_between(start_date="-2y", end_date="-1m")
    duration = timedelta(days=random.randint(60, 365))
    end = start + duration
    status = random.choice(["En cours", "Terminé", "En pause"])
    
    projects.append({
        "id": proj_id,
        "name": f"Projet {fake.word().capitalize()}",
        "description": fake.sentence(),
        "start_date": start.isoformat(),
        "deadline": end.isoformat(),
        "status": status
    })
    
    # Generate 10 to 30 tasks per project
    for t in range(random.randint(10, 30)):
        task_status = "Terminé" if status == "Terminé" else random.choice(["À faire", "En cours", "En revue", "Terminé"])
        eval_score = random.randint(60, 100) if task_status == "Terminé" else ""
        
        tasks.append({
            "id": fake.uuid4(),
            "project_id": proj_id,
            "assignee_id": random.choice(employees)["id"],
            "title": fake.catch_phrase(),
            "description": fake.sentence(),
            "status": task_status,
            "due_date": (start + timedelta(days=random.randint(10, 60))).isoformat(),
            "evaluation_score": eval_score
        })

with open("data_imports/06_projects.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "description", "start_date", "deadline", "status"])
    writer.writeheader()
    for p in projects:
        writer.writerow(p)

with open("data_imports/07_tasks.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "project_id", "assignee_id", "title", "description", "status", "due_date", "evaluation_score"])
    writer.writeheader()
    for t in tasks:
        writer.writerow(t)

print("Data generation complete! Files saved in 'data_imports/' folder.")

# ---------------------------------------------------------
# 7. Attendances (Présences)
# ---------------------------------------------------------
print("Generating 08_attendances.csv")
attendances = []

# Generate attendances for the last 30 days for all active employees
start_date_att = datetime.now() - timedelta(days=30)
for emp in employees:
    if emp["status"] == "actif":
        for day_offset in range(30):
            current_date = start_date_att + timedelta(days=day_offset)
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() >= 5:
                continue
            
            # Determine status
            # 90% Present, 5% Retard, 5% Absent
            status = random.choices(["Présent", "Retard", "Absent"], weights=[90, 5, 5])[0]
            
            check_in_str = ""
            check_out_str = ""
            
            if status == "Présent":
                # Check-in between 8:00 and 9:00
                check_in_time = current_date.replace(hour=8, minute=random.randint(0, 59))
                # Check-out between 17:00 and 19:00
                check_out_time = current_date.replace(hour=random.randint(17, 18), minute=random.randint(0, 59))
                check_in_str = check_in_time.isoformat()
                check_out_str = check_out_time.isoformat()
            elif status == "Retard":
                # Check-in between 9:01 and 11:00
                check_in_time = current_date.replace(hour=random.randint(9, 10), minute=random.randint(1, 59))
                check_out_time = current_date.replace(hour=random.randint(17, 18), minute=random.randint(0, 59))
                check_in_str = check_in_time.isoformat()
                check_out_str = check_out_time.isoformat()

            attendances.append({
                "id": fake.uuid4(),
                "employee_id": emp["id"],
                "date": current_date.date().isoformat(),
                "check_in": check_in_str,
                "check_out": check_out_str,
                "status": status
            })

with open("data_imports/08_attendances.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "date", "check_in", "check_out", "status"])
    writer.writeheader()
    for a in attendances:
        writer.writerow(a)

print("Attendance generation complete!")

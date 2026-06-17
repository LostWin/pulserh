"""
Script de génération de données CSV réalistes pour PulseAI.
Produit ~100 employés avec 3-5 ans d'historique d'entreprise.
Tous les fichiers sont compatibles avec le module d'import PulseAI.
"""
import os
import csv
import json
import random
import re
import uuid
from datetime import datetime, timedelta, timezone, date
from faker import Faker
try:
    from scripts.demo_identity_data import DEMO_USERS
except ModuleNotFoundError:
    from demo_identity_data import DEMO_USERS

# Use multiple locales to mix names
fake = Faker(['ar_AA', 'fr_FR', 'en_US'])
Faker.seed(42)
random.seed(42)

# Ensure the output directory exists
os.makedirs("data_imports", exist_ok=True)

# ── Constants ──
NUM_EMPLOYEES = 100
HISTORY_YEARS = 5  # how far back hire dates can go
ATTENDANCE_YEARS = 3  # years of attendance data
COMPANY_START = date(2021, 6, 1)  # company founding ~5 years ago
TODAY = date.today()

# ── Helpers ──
def date_str(d) -> str:
    """Format a date object as YYYY-MM-DD string."""
    if isinstance(d, datetime):
        return d.date().isoformat()
    return d.isoformat()

def datetime_str(dt) -> str:
    """Format a datetime object as ISO-8601 string with timezone."""
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime.combine(dt, datetime.min.time(), tzinfo=timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

def random_date(start: date, end: date) -> date:
    """Random date between start and end inclusive."""
    delta = (end - start).days
    if delta <= 0:
        return start
    return start + timedelta(days=random.randint(0, delta))

def random_hire_date() -> date:
    """Random hire date between company start and 3 months ago."""
    return random_date(COMPANY_START, TODAY - timedelta(days=90))

def gen_id() -> str:
    return str(uuid.uuid4())

print("=" * 60)
print("PulseAI — Génération de données CSV réalistes")
print(f"  Employés: ~{NUM_EMPLOYEES} + {len(DEMO_USERS)} démo")
print(f"  Historique: {HISTORY_YEARS} ans")
print(f"  Présences: {ATTENDANCE_YEARS} ans")
print("=" * 60)

# ---------------------------------------------------------
# 1. Departments & Jobs Definitions
# ---------------------------------------------------------
print("\n[1/21] Départements & Postes...")

departments_data = {
    "dep-1": {
        "name": "Ressources Humaines",
        "jobs": [
            {"title": "Directeur RH", "level": "Executive"},
            {"title": "Responsable RH", "level": "Senior"},
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
            {"title": "Engineering Manager", "level": "Senior"},
            {"title": "Lead Développeur", "level": "Senior"},
            {"title": "Développeur Backend", "level": "Mid"},
            {"title": "Développeur Frontend", "level": "Mid"},
            {"title": "Ingénieur DevOps", "level": "Senior"},
            {"title": "Software Engineer", "level": "Mid"},
            {"title": "Administrateur Système", "level": "Senior"},
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
            {"title": "Directrice des opérations RH", "level": "Executive"},
            {"title": "COO", "level": "Executive"},
            {"title": "Assistant de Direction", "level": "Mid"}
        ]
    }
}

departments = []
jobs = []
dep_to_jobs = {}
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

# ---------------------------------------------------------
# 2. Employees
# ---------------------------------------------------------
print("[2/21] Employés...")

employees = []
managers_pool = []
dep_ids = list(dep_to_jobs.keys())
department_by_name = {dep_info["name"]: dep_id for dep_id, dep_info in departments_data.items()}
job_id_by_title = {job["title"]: job["id"] for job in jobs}

demo_employee_by_email = {}
for demo in DEMO_USERS:
    dep_id = department_by_name[demo["department"]]
    job_id = job_id_by_title[demo["job_title"]]
    employee_row = {
        "id": demo["id"],
        "user_id": "",
        "first_name": demo["first_name"],
        "last_name": demo["last_name"],
        "email": demo["email"],
        "phone": fake.phone_number(),
        "hire_date": date_str(demo["hire_date"]),
        "status": demo["status"],
        "department_id": dep_id,
        "job_id": job_id,
        "manager_id": "",
    }
    employees.append(employee_row)
    demo_employee_by_email[demo["email"]] = employee_row
    if demo["manager_email"] is None or any(keyword in demo["job_title"] for keyword in ["Manager", "Responsable", "Direct", "Admin"]):
        managers_pool.append(employee_row["id"])

for demo in DEMO_USERS:
    if demo["manager_email"]:
        demo_employee_by_email[demo["email"]]["manager_id"] = demo_employee_by_email[demo["manager_email"]]["id"]

moroccan_first_names_m = ["Amine", "Youssef", "Mehdi", "Hamza", "Karim", "Oussama", "Ayoub", "Walid", "Anas", "Omar", "Ilias", "Nizar", "Rachid", "Tariq", "Hicham", "Adil", "Saad", "Bilal", "Zakaria", "Driss"]
moroccan_first_names_f = ["Fatima", "Salma", "Imane", "Hajar", "Meryem", "Sara", "Khaoula", "Kenza", "Nada", "Zineb", "Laila", "Amina", "Hanane", "Soukaina", "Rim"]
moroccan_last_names = ["Alaoui", "Benali", "Chraibi", "Berrada", "Tazi", "Bennani", "El Fassi", "Guessous", "Lahlou", "El Idrissi", "Mansouri", "Tahiri", "Amrani", "El Malki", "Daoudi", "Bouzid", "El Amrani", "Zerouali", "Bouazza", "Cherkaoui"]

# Generate statuses: 10% will have departed (inactive) to give churn model something to learn
status_weights = [82, 10, 5, 3]  # actif, inactif, suspendu, parti
status_options = ["actif", "inactif", "suspendu", "inactif"]

for i in range(1, NUM_EMPLOYEES + 1):
    emp_id = f"emp-{i}"
    is_female = random.random() < 0.45
    first_name = random.choice(moroccan_first_names_f if is_female else moroccan_first_names_m)
    last_name = random.choice(moroccan_last_names)

    base_email = f"{first_name}.{last_name}".lower()
    clean_prefix = re.sub(r"[^a-z0-9]", "", base_email.replace(".", ""))
    if not clean_prefix:
        clean_prefix = "user"
    email_clean = f"{clean_prefix}.{str(uuid.uuid4())[:6]}@pulse.com"

    # First 20 are potential managers
    manager_id = ""
    if i > 20:
        manager_id = random.choice(managers_pool)
    else:
        managers_pool.append(emp_id)

    dep_id = random.choice(dep_ids)
    job_id = random.choice(dep_to_jobs[dep_id])
    hire = random_hire_date()
    status = random.choices(status_options, weights=status_weights)[0]

    employees.append({
        "id": emp_id,
        "user_id": "",
        "first_name": first_name,
        "last_name": last_name,
        "email": email_clean,
        "phone": fake.phone_number(),
        "hire_date": date_str(hire),
        "status": status,
        "department_id": dep_id,
        "job_id": job_id,
        "manager_id": manager_id
    })

# Reassign some employees to specific departments for demo coherence
non_demo_employees = [e for e in employees if not e["id"].startswith("emp-demo-")]
fatima_id = demo_employee_by_email["fatima.alaoui@pulse.ma"]["id"]
sara_id = demo_employee_by_email["sara.bennani@pulse.ma"]["id"]
it_dep_id = department_by_name["IT & Engineering"]
for member in non_demo_employees[:6]:
    member["department_id"] = it_dep_id
    member["manager_id"] = fatima_id
for member in non_demo_employees[6:9]:
    member["manager_id"] = sara_id

# Update department managers
for d in departments:
    dept_employees = [e for e in employees if e["department_id"] == d["id"]]
    if d["name"] == "Ressources Humaines":
        d["manager_id"] = demo_employee_by_email["karim.tazi@pulse.ma"]["id"]
    elif d["name"] == "IT & Engineering":
        d["manager_id"] = fatima_id
    elif d["name"] == "Direction Générale":
        d["manager_id"] = sara_id
    elif dept_employees:
        d["manager_id"] = random.choice(dept_employees)["id"]

# Write departments
with open("data_imports/01_departments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "manager_id"])
    writer.writeheader()
    for d in departments:
        writer.writerow(d)

# Write jobs
with open("data_imports/02_jobs.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "title", "level", "description"])
    writer.writeheader()
    for j in jobs:
        writer.writerow(j)

# Write employees
with open("data_imports/03_employees.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "user_id", "first_name", "last_name", "email", "phone", "hire_date", "status", "department_id", "job_id", "manager_id"])
    writer.writeheader()
    for e in employees:
        writer.writerow(e)

print(f"  → {len(employees)} employés générés")

# ---------------------------------------------------------
# 3. Contracts (with history)
# ---------------------------------------------------------
print("[3/21] Contrats...")
contracts = []
for emp in employees:
    hire = date.fromisoformat(emp["hire_date"])
    has_history = random.random() > 0.7

    if has_history:
        cdd_duration = timedelta(days=random.randint(180, 365))
        cdd_end = hire + cdd_duration
        contracts.append({
            "id": gen_id(),
            "employee_id": emp["id"],
            "contract_type": "CDD",
            "start_date": date_str(hire),
            "end_date": date_str(cdd_end),
            "salary": random.randint(28000, 42000),
            "is_active": "false"
        })
        current_start = cdd_end + timedelta(days=1)
    else:
        current_start = hire

    is_active = emp["status"] == "actif"
    salary_by_level = {"Junior": (30000, 42000), "Mid": (40000, 60000), "Senior": (55000, 80000), "Executive": (75000, 120000)}
    job_obj = next((j for j in jobs if j["id"] == emp["job_id"]), None)
    level = job_obj["level"] if job_obj else "Mid"
    salary_range = salary_by_level.get(level, (40000, 60000))

    contracts.append({
        "id": gen_id(),
        "employee_id": emp["id"],
        "contract_type": "CDI",
        "start_date": date_str(current_start),
        "end_date": "",
        "salary": random.randint(*salary_range),
        "is_active": str(is_active).lower()
    })

# Override demo user contracts
for demo in DEMO_USERS:
    row = demo_employee_by_email[demo["email"]]
    contracts = [c for c in contracts if not (c["employee_id"] == row["id"] and c["is_active"] == "true")]
    contracts.append({
        "id": f"contract-{row['id']}",
        "employee_id": row["id"],
        "contract_type": demo["contract_type"],
        "start_date": date_str(demo["hire_date"]),
        "end_date": "",
        "salary": demo["salary"],
        "is_active": "true",
    })

with open("data_imports/04_contracts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "contract_type", "start_date", "end_date", "salary", "is_active"])
    writer.writeheader()
    for c in contracts:
        writer.writerow(c)

print(f"  → {len(contracts)} contrats générés")

# ---------------------------------------------------------
# 4. Leaves (5 years of history)
# ---------------------------------------------------------
print("[4/21] Congés (5 ans d'historique)...")
leave_types = ["Congés Payés", "Maladie", "Maternité/Paternité", "Autres", "Raisons personnelles"]
leave_type_weights = [55, 20, 5, 10, 10]
leaves = []

for emp in employees:
    hire = date.fromisoformat(emp["hire_date"])
    # Generate leaves from hire date to today
    current_year_start = max(hire, COMPANY_START)
    year = current_year_start.year

    while year <= TODAY.year:
        year_start = date(year, 1, 1) if year > current_year_start.year else current_year_start
        year_end = date(year, 12, 31) if year < TODAY.year else TODAY

        if (year_end - year_start).days < 30:
            year += 1
            continue

        # 3-8 leave entries per year for active employees
        num_leaves = random.randint(2, 7) if emp["status"] == "actif" else random.randint(0, 3)
        for _ in range(num_leaves):
            start = random_date(year_start, year_end - timedelta(days=1))
            duration = random.choices(
                [1, 2, 3, 5, 7, 10, 14],
                weights=[15, 20, 15, 20, 15, 10, 5]
            )[0]
            end = start + timedelta(days=duration)

            leave_type = random.choices(leave_types, weights=leave_type_weights)[0]
            # Past leaves are mostly approved; future leaves are pending
            if end < TODAY:
                status = random.choices(["Approuvé", "Rejeté"], weights=[92, 8])[0]
            else:
                status = random.choices(["Approuvé", "En attente", "Rejeté"], weights=[50, 40, 10])[0]

            reasons = {
                "Congés Payés": random.choice(["Vacances", "Vacances familiales", "Repos", "Voyage"]),
                "Maladie": random.choice(["Consultation médicale", "Grippe", "Repos médical"]),
                "Maternité/Paternité": "Congé parental",
                "Autres": random.choice(["Déménagement", "Événement familial", "Formation externe"]),
                "Raisons personnelles": "Raisons personnelles",
            }

            leaves.append({
                "id": gen_id(),
                "employee_id": emp["id"],
                "start_date": date_str(start),
                "end_date": date_str(end),
                "leave_type": leave_type,
                "status": status,
                "reason": reasons[leave_type]
            })
        year += 1

# Demo leave
leaves.append({
    "id": "leave-demo-youssef",
    "employee_id": demo_employee_by_email["youssef.benali@pulse.ma"]["id"],
    "start_date": date_str(TODAY + timedelta(days=15)),
    "end_date": date_str(TODAY + timedelta(days=17)),
    "leave_type": "Congés Payés",
    "status": "En attente",
    "reason": "Vacances d'été",
})

with open("data_imports/05_leaves.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "start_date", "end_date", "leave_type", "status", "reason"])
    writer.writeheader()
    for leave in leaves:
        writer.writerow(leave)

print(f"  → {len(leaves)} congés générés")

# ---------------------------------------------------------
# 5. Projects & Tasks (more projects, deeper history)
# ---------------------------------------------------------
print("[5/21] Projets & Tâches...")
projects = []
tasks = []

# Demo project
projects.append({
    "id": "proj-demo-onboarding",
    "name": "Onboarding Demo",
    "description": "Projet support pour les tâches de démo et l'intégration collaborateur.",
    "start_date": date_str(TODAY - timedelta(days=7)),
    "deadline": date_str(TODAY + timedelta(days=30)),
    "status": "En cours",
    "priority": "Haute",
    "business_domain": "People Operations",
    "required_skill_ids": "skill-onboarding,skill-communication,skill-security",
    "manager_id": fatima_id,
})
tasks.extend([
    {
        "id": "task-demo-setup",
        "project_id": "proj-demo-onboarding",
        "assignee_id": demo_employee_by_email["youssef.benali@pulse.ma"]["id"],
        "title": "Configurer le poste de travail",
        "description": "Installation des outils internes et accès.",
        "status": "À faire",
        "due_date": date_str(TODAY + timedelta(days=2)),
        "evaluation_score": "",
    },
    {
        "id": "task-demo-manager-meeting",
        "project_id": "proj-demo-onboarding",
        "assignee_id": demo_employee_by_email["youssef.benali@pulse.ma"]["id"],
        "title": "Rencontre avec le manager",
        "description": "Point d'intégration avec Fatima Alaoui.",
        "status": "À faire",
        "due_date": date_str(TODAY + timedelta(days=1)),
        "evaluation_score": "",
    },
])

project_names = [
    "Refonte Portail RH", "Migration Cloud", "Analytics Dashboard", "Sécurité RGPD",
    "Onboarding Automatisé", "Plan de Formation 2024", "Audit Qualité", "CRM Interne",
    "App Mobile", "Refonte SI Paie", "Data Warehouse", "Chatbot RH",
    "Programme Mentorat", "Digitalisation Processus", "Certification ISO",
    "Plan Succession", "Bien-Être au Travail", "Marque Employeur",
    "Optimisation Recrutement", "Intégration ERP", "Plateforme E-Learning",
    "Gestion des Talents", "Restructuration Org", "Innovation Lab"
]

skill_pool = ["skill-react", "skill-python", "skill-management", "skill-security", "skill-communication", "skill-data"]
project_statuses = ["En cours", "Terminé", "En pause"]

for i, proj_name in enumerate(project_names, 1):
    proj_id = f"proj-{i}"
    start = random_date(COMPANY_START, TODAY - timedelta(days=60))
    duration = timedelta(days=random.randint(90, 540))
    deadline = start + duration
    status = random.choices(project_statuses, weights=[40, 50, 10])[0]
    if deadline < TODAY - timedelta(days=30):
        status = "Terminé"

    projects.append({
        "id": proj_id,
        "name": proj_name,
        "description": f"Projet {proj_name} — initiative stratégique de l'entreprise.",
        "start_date": date_str(start),
        "deadline": date_str(deadline),
        "status": status,
        "priority": random.choice(["Basse", "Moyenne", "Haute", "Critique"]),
        "business_domain": random.choice(["People Analytics", "Engineering", "Operations", "Finance", "Talent", "Compliance"]),
        "required_skill_ids": ",".join(random.sample(skill_pool, k=random.randint(1, 3))),
        "manager_id": random.choice(employees)["id"],
    })

    # 8-25 tasks per project
    num_tasks = random.randint(8, 25)
    for t in range(num_tasks):
        task_status = "Terminé" if status == "Terminé" else random.choice(["À faire", "En cours", "En revue", "Terminé"])
        eval_score = random.randint(55, 100) if task_status == "Terminé" else ""

        tasks.append({
            "id": gen_id(),
            "project_id": proj_id,
            "assignee_id": random.choice(employees)["id"],
            "title": fake.catch_phrase(),
            "description": fake.sentence(),
            "status": task_status,
            "due_date": date_str(start + timedelta(days=random.randint(10, max(11, (deadline - start).days)))),
            "evaluation_score": eval_score
        })

with open("data_imports/06_projects.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "description", "start_date", "deadline", "status", "priority", "business_domain", "required_skill_ids", "manager_id"])
    writer.writeheader()
    for p in projects:
        writer.writerow(p)

with open("data_imports/07_tasks.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "project_id", "assignee_id", "title", "description", "status", "due_date", "evaluation_score"])
    writer.writeheader()
    for t in tasks:
        writer.writerow(t)

print(f"  → {len(projects)} projets, {len(tasks)} tâches générés")

# ---------------------------------------------------------
# 6. Attendances (3 years of daily data)
# ---------------------------------------------------------
print("[6/21] Présences (3 ans)... (cela peut prendre quelques secondes)")
attendances = []
att_start = TODAY - timedelta(days=ATTENDANCE_YEARS * 365)

for emp in employees:
    hire = date.fromisoformat(emp["hire_date"])
    emp_att_start = max(hire, att_start)

    if emp["status"] in ("inactif",):
        # Inactive employees: generate attendance until a random departure date
        departure = random_date(emp_att_start + timedelta(days=180), TODAY - timedelta(days=30))
        emp_att_end = departure
    else:
        emp_att_end = TODAY

    # Create a set of leave dates for this employee to mark as absent
    emp_leave_dates = set()
    for leave in leaves:
        if leave["employee_id"] == emp["id"] and leave["status"] == "Approuvé":
            ls = date.fromisoformat(leave["start_date"])
            le = date.fromisoformat(leave["end_date"])
            d = ls
            while d <= le:
                emp_leave_dates.add(d)
                d += timedelta(days=1)

    current = emp_att_start
    while current <= emp_att_end:
        # Skip weekends
        if current.weekday() >= 5:
            current += timedelta(days=1)
            continue

        if current in emp_leave_dates:
            attendances.append({
                "id": gen_id(),
                "employee_id": emp["id"],
                "date": date_str(current),
                "check_in": "",
                "check_out": "",
                "status": "Absent"
            })
        else:
            status = random.choices(["Présent", "Retard", "Absent"], weights=[92, 5, 3])[0]
            check_in_str = ""
            check_out_str = ""

            if status == "Présent":
                ci = datetime(current.year, current.month, current.day, 8, random.randint(0, 55), tzinfo=timezone.utc)
                co = datetime(current.year, current.month, current.day, random.randint(17, 18), random.randint(0, 55), tzinfo=timezone.utc)
                check_in_str = datetime_str(ci)
                check_out_str = datetime_str(co)
            elif status == "Retard":
                ci = datetime(current.year, current.month, current.day, random.randint(9, 10), random.randint(1, 55), tzinfo=timezone.utc)
                co = datetime(current.year, current.month, current.day, random.randint(17, 19), random.randint(0, 55), tzinfo=timezone.utc)
                check_in_str = datetime_str(ci)
                check_out_str = datetime_str(co)

            attendances.append({
                "id": gen_id(),
                "employee_id": emp["id"],
                "date": date_str(current),
                "check_in": check_in_str,
                "check_out": check_out_str,
                "status": status
            })

        current += timedelta(days=1)

with open("data_imports/08_attendances.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "date", "check_in", "check_out", "status"])
    writer.writeheader()
    for a in attendances:
        writer.writerow(a)

print(f"  → {len(attendances)} lignes de présence générées")

# ---------------------------------------------------------
# 7. Skills
# ---------------------------------------------------------
print("[7/21] Compétences...")

skills = [
    {"id": "skill-react", "name": "React", "category": "Engineering", "description": "Développement frontend React.", "level_scale": "beginner-intermediate-advanced-expert", "is_certifiable": "false", "is_active": "true"},
    {"id": "skill-python", "name": "Python", "category": "Engineering", "description": "Développement backend et data.", "level_scale": "beginner-intermediate-advanced-expert", "is_certifiable": "false", "is_active": "true"},
    {"id": "skill-onboarding", "name": "Onboarding", "category": "People", "description": "Conception de parcours d'intégration.", "level_scale": "foundation-operational-strategic", "is_certifiable": "false", "is_active": "true"},
    {"id": "skill-payroll", "name": "Paie", "category": "RH", "description": "Gestion des opérations de paie.", "level_scale": "beginner-intermediate-advanced-expert", "is_certifiable": "true", "is_active": "true"},
    {"id": "skill-management", "name": "Management", "category": "Leadership", "description": "Pilotage d'équipe et accompagnement.", "level_scale": "beginner-intermediate-advanced-expert", "is_certifiable": "false", "is_active": "true"},
    {"id": "skill-security", "name": "Sécurité & RGPD", "category": "Compliance", "description": "Bonnes pratiques sécurité et confidentialité.", "level_scale": "foundation-operational-expert", "is_certifiable": "true", "is_active": "true"},
    {"id": "skill-communication", "name": "Communication", "category": "Soft Skills", "description": "Communication écrite et orale.", "level_scale": "beginner-intermediate-advanced-expert", "is_certifiable": "false", "is_active": "true"},
    {"id": "skill-data", "name": "Data Analysis", "category": "Analytics", "description": "Analyse et interprétation de données RH.", "level_scale": "beginner-intermediate-advanced-expert", "is_certifiable": "false", "is_active": "true"},
]

skill_ids = [s["id"] for s in skills]

with open("data_imports/09_skills.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "category", "description", "level_scale", "is_certifiable", "is_active"])
    writer.writeheader()
    for row in skills:
        writer.writerow(row)

# ---------------------------------------------------------
# 8. Employee Skills
# ---------------------------------------------------------
print("[8/21] Compétences employés...")
employee_skills = []

for emp in employees:
    if emp["job_id"] in {job_id_by_title.get("Software Engineer"), job_id_by_title.get("Développeur Frontend"), job_id_by_title.get("Développeur Backend")}:
        selected_skills = ["skill-react", "skill-python", "skill-security"]
    elif emp["job_id"] == job_id_by_title.get("Engineering Manager"):
        selected_skills = ["skill-management", "skill-communication", "skill-security"]
    elif emp["department_id"] == department_by_name["Ressources Humaines"]:
        selected_skills = ["skill-onboarding", "skill-payroll", "skill-security"]
    else:
        selected_skills = random.sample(skill_ids, k=min(3, len(skill_ids)))

    for si, skill_id in enumerate(selected_skills):
        employee_skills.append({
            "id": f"employee-skill-{emp['id']}-{si + 1}",
            "employee_id": emp["id"],
            "skill_id": skill_id,
            "proficiency_level": random.choice(["beginner", "intermediate", "advanced", "expert"]),
            "years_experience": round(random.uniform(0.5, 8.0), 1),
            "is_primary": "true" if si == 0 else "false",
            "last_assessed_at": datetime_str(datetime.now(timezone.utc) - timedelta(days=random.randint(15, 220))),
            "source": "import_seed",
            "validated_by": "Pulse RH",
            "validated_at": datetime_str(datetime.now(timezone.utc) - timedelta(days=random.randint(5, 90))),
            "last_used_at": datetime_str(datetime.now(timezone.utc) - timedelta(days=random.randint(1, 45))),
            "confidence_score": round(random.uniform(65.0, 98.0), 1),
        })

with open("data_imports/10_employee_skills.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "skill_id", "proficiency_level", "years_experience", "is_primary", "last_assessed_at", "source", "validated_by", "validated_at", "last_used_at", "confidence_score"])
    writer.writeheader()
    for row in employee_skills:
        writer.writerow(row)

print(f"  → {len(employee_skills)} compétences employés")

# ---------------------------------------------------------
# 9. Training Courses
# ---------------------------------------------------------
print("[9/21] Formations...")

training_courses = [
    {"id": "training-rgpd", "title": "Parcours sécurité & RGPD", "provider": "Pulse Academy", "duration_hours": 3, "level": "Foundation", "format": "e-learning", "description": "Formation obligatoire sur la sécurité et la confidentialité.", "target_skill_id": "skill-security", "required_for_job_family": "", "difficulty": "Foundation", "delivery_mode": "e-learning", "mandatory_for_roles": "collaborator,manager,hr,director,admin"},
    {"id": "training-react", "title": "React avancé", "provider": "Pulse Academy", "duration_hours": 6, "level": "Advanced", "format": "blended", "description": "Perfectionnement React orienté produit.", "target_skill_id": "skill-react", "required_for_job_family": "Software Engineer", "difficulty": "Advanced", "delivery_mode": "blended", "mandatory_for_roles": ""},
    {"id": "training-manager-101", "title": "Manager 101", "provider": "People Ops", "duration_hours": 4, "level": "Intermediate", "format": "présentiel", "description": "Fondamentaux du management de proximité.", "target_skill_id": "skill-management", "required_for_job_family": "Engineering Manager", "difficulty": "Intermediate", "delivery_mode": "présentiel", "mandatory_for_roles": "manager"},
    {"id": "training-onboarding", "title": "Concevoir un onboarding impactant", "provider": "People Ops", "duration_hours": 5, "level": "Intermediate", "format": "e-learning", "description": "Structurer un onboarding personnalisé et mesurable.", "target_skill_id": "skill-onboarding", "required_for_job_family": "Responsable RH", "difficulty": "Intermediate", "delivery_mode": "e-learning", "mandatory_for_roles": "hr"},
    {"id": "training-python-data", "title": "Python pour l'analyse de données", "provider": "DataCamp", "duration_hours": 8, "level": "Intermediate", "format": "e-learning", "description": "Maîtriser pandas, numpy et la visualisation.", "target_skill_id": "skill-python", "required_for_job_family": "Data Scientist", "difficulty": "Intermediate", "delivery_mode": "e-learning", "mandatory_for_roles": ""},
    {"id": "training-communication", "title": "Communication efficace en entreprise", "provider": "Pulse Academy", "duration_hours": 3, "level": "Foundation", "format": "présentiel", "description": "Techniques de communication professionnelle.", "target_skill_id": "skill-communication", "required_for_job_family": "", "difficulty": "Foundation", "delivery_mode": "présentiel", "mandatory_for_roles": ""},
]

with open("data_imports/11_training_courses.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "title", "provider", "duration_hours", "level", "format", "description", "target_skill_id", "required_for_job_family", "difficulty", "delivery_mode", "mandatory_for_roles"])
    writer.writeheader()
    for row in training_courses:
        writer.writerow(row)

# ---------------------------------------------------------
# 10. Training Enrollments
# ---------------------------------------------------------
print("[10/21] Inscriptions formations...")
training_enrollments = []
training_ids = [tc["id"] for tc in training_courses]

for emp in employees:
    # RGPD mandatory for everyone
    rgpd_completed = emp["status"] == "actif" and random.random() > 0.15
    training_enrollments.append({
        "id": f"training-enrollment-rgpd-{emp['id']}",
        "employee_id": emp["id"],
        "training_id": "training-rgpd",
        "status": "completed" if rgpd_completed else "assigned",
        "assigned_at": datetime_str(datetime.now(timezone.utc) - timedelta(days=random.randint(60, 400))),
        "due_date": date_str(TODAY + timedelta(days=20)),
        "completed_at": datetime_str(datetime.now(timezone.utc) - timedelta(days=random.randint(1, 50))) if rgpd_completed else "",
        "score": random.randint(72, 98) if rgpd_completed else "",
        "mandatory": "true",
        "assigned_by": "Pulse RH",
        "recommendation_reason": "Parcours de conformité obligatoire",
    })

    # Random extra enrollments
    if random.random() > 0.4:
        extra_training = random.choice([t for t in training_ids if t != "training-rgpd"])
        extra_status = random.choice(["assigned", "in_progress", "completed"])
        training_enrollments.append({
            "id": gen_id(),
            "employee_id": emp["id"],
            "training_id": extra_training,
            "status": extra_status,
            "assigned_at": datetime_str(datetime.now(timezone.utc) - timedelta(days=random.randint(10, 200))),
            "due_date": date_str(TODAY + timedelta(days=random.randint(10, 90))),
            "completed_at": datetime_str(datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))) if extra_status == "completed" else "",
            "score": random.randint(60, 98) if extra_status == "completed" else "",
            "mandatory": "false",
            "assigned_by": random.choice(["Manager direct", "Pulse RH", "Auto-inscription"]),
            "recommendation_reason": random.choice(["Montée en compétence", "Projet actif", "Plan de développement", "Curiosité personnelle"]),
        })

# Demo-specific enrollments
for demo in DEMO_USERS:
    eid = demo_employee_by_email[demo["email"]]["id"]
    if demo["email"] == "youssef.benali@pulse.ma":
        training_enrollments.append({
            "id": "training-enrollment-youssef-react",
            "employee_id": eid,
            "training_id": "training-react",
            "status": "in_progress",
            "assigned_at": datetime_str(datetime.now(timezone.utc) - timedelta(days=3)),
            "due_date": date_str(TODAY + timedelta(days=14)),
            "completed_at": "",
            "score": "",
            "mandatory": "false",
            "assigned_by": "Fatima Alaoui",
            "recommendation_reason": "Projet frontend actif et montée en compétence produit",
        })
    if demo["email"] == "fatima.alaoui@pulse.ma":
        training_enrollments.append({
            "id": "training-enrollment-fatima-manager",
            "employee_id": eid,
            "training_id": "training-manager-101",
            "status": "completed",
            "assigned_at": datetime_str(datetime.now(timezone.utc) - timedelta(days=35)),
            "due_date": date_str(TODAY - timedelta(days=5)),
            "completed_at": datetime_str(datetime.now(timezone.utc) - timedelta(days=8)),
            "score": 91,
            "mandatory": "true",
            "assigned_by": "Karim Tazi",
            "recommendation_reason": "Prise de poste managériale",
        })
    if demo["email"] == "karim.tazi@pulse.ma":
        training_enrollments.append({
            "id": "training-enrollment-karim-onboarding",
            "employee_id": eid,
            "training_id": "training-onboarding",
            "status": "completed",
            "assigned_at": datetime_str(datetime.now(timezone.utc) - timedelta(days=28)),
            "due_date": date_str(TODAY - timedelta(days=2)),
            "completed_at": datetime_str(datetime.now(timezone.utc) - timedelta(days=4)),
            "score": 95,
            "mandatory": "true",
            "assigned_by": "Karim Tazi",
            "recommendation_reason": "Montée en compétence RH sur les parcours d'intégration",
        })

with open("data_imports/12_training_enrollments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "training_id", "status", "assigned_at", "due_date", "completed_at", "score", "mandatory", "assigned_by", "recommendation_reason"])
    writer.writeheader()
    for row in training_enrollments:
        writer.writerow(row)

print(f"  → {len(training_enrollments)} inscriptions formations")

# ---------------------------------------------------------
# 11. Project Assignments
# ---------------------------------------------------------
print("[11/21] Affectations projets...")
project_assignments = []
project_ids = [p["id"] for p in projects]

for emp in employees:
    num_assignments = 2 if emp["status"] == "actif" else 1
    assigned_projects = random.sample(project_ids, k=min(num_assignments, len(project_ids)))
    for ai, pid in enumerate(assigned_projects):
        project_assignments.append({
            "id": f"assignment-{emp['id']}-{ai + 1}",
            "project_id": pid,
            "employee_id": emp["id"],
            "role_on_project": "Contributeur" if ai else "Référent",
            "allocation_pct": 60 if ai == 0 else 30,
            "start_date": date_str(random_date(TODAY - timedelta(days=180), TODAY - timedelta(days=10))),
            "end_date": "",
            "is_active": "true",
        })

with open("data_imports/13_project_assignments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "project_id", "employee_id", "role_on_project", "allocation_pct", "start_date", "end_date", "is_active"])
    writer.writeheader()
    for row in project_assignments:
        writer.writerow(row)

print(f"  → {len(project_assignments)} affectations")

# ---------------------------------------------------------
# 12. Engagement Snapshots (monthly for 3 years)
# ---------------------------------------------------------
print("[12/21] Snapshots d'engagement (mensuels, 3 ans)...")
engagement_snapshots = []

for emp in employees:
    hire = date.fromisoformat(emp["hire_date"])
    snap_start = max(hire, TODAY - timedelta(days=ATTENDANCE_YEARS * 365))

    # Base engagement score influenced by status
    if emp["status"] == "actif":
        base_score = random.randint(62, 88)
    elif emp["status"] == "inactif":
        base_score = random.randint(40, 60)
    else:
        base_score = random.randint(50, 70)

    # Demo overrides
    if emp["id"] == demo_employee_by_email.get("youssef.benali@pulse.ma", {}).get("id"):
        base_score = 84
    elif emp["id"] == demo_employee_by_email.get("fatima.alaoui@pulse.ma", {}).get("id"):
        base_score = 79
    elif emp["id"] == demo_employee_by_email.get("karim.tazi@pulse.ma", {}).get("id"):
        base_score = 82

    current_month = date(snap_start.year, snap_start.month, 1)
    prev_score = base_score
    month_index = 0

    while current_month <= TODAY:
        # Natural drift with some noise
        drift = random.randint(-4, 4)
        score = max(30, min(98, prev_score + drift))
        trend = score - prev_score
        risk_band = "high" if score < 55 else "medium" if score < 72 else "low"

        engagement_snapshots.append({
            "id": f"engagement-{emp['id']}-{month_index}",
            "employee_id": emp["id"],
            "score": score,
            "source": random.choice(["pulse", "survey", "manager_review"]),
            "pulse_label": random.choice(["stable", "engaged", "watch", "boost"]),
            "comment": "Mesure mensuelle d'engagement.",
            "trend": trend,
            "risk_band": risk_band,
            "source_signals": json.dumps({
                "absences_30j": random.randint(0, 3),
                "overdue_tasks": random.randint(0, 4),
                "mandatory_training_gap": random.randint(0, 1),
                "active_projects": random.randint(1, 3),
            }, ensure_ascii=False),
            "captured_at": datetime_str(datetime(current_month.year, current_month.month, 15, 10, 0, tzinfo=timezone.utc)),
        })

        prev_score = score
        month_index += 1
        # Advance to next month
        if current_month.month == 12:
            current_month = date(current_month.year + 1, 1, 1)
        else:
            current_month = date(current_month.year, current_month.month + 1, 1)

with open("data_imports/14_engagement_snapshots.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "score", "source", "pulse_label", "comment", "trend", "risk_band", "source_signals", "captured_at"])
    writer.writeheader()
    for row in engagement_snapshots:
        writer.writerow(row)

print(f"  → {len(engagement_snapshots)} snapshots d'engagement")

# ---------------------------------------------------------
# 13. Performance Reviews (multi-period)
# ---------------------------------------------------------
print("[13/21] Revues de performance (multi-périodes)...")
performance_reviews = []
review_periods = []
for y in range(COMPANY_START.year, TODAY.year + 1):
    review_periods.append(f"{y}-S1")
    if y < TODAY.year or (y == TODAY.year and TODAY.month > 6):
        review_periods.append(f"{y}-S2")

strength_options = [
    "Bonne autonomie et collaboration transverse.",
    "Excellente capacité d'exécution sur les sujets prioritaires.",
    "Communication claire et fiable avec l'équipe.",
    "Forte capacité d'adaptation au changement.",
    "Rigueur et attention au détail remarquables.",
    "Leadership naturel et esprit d'initiative.",
]
improvement_options = [
    "Structurer davantage la priorisation hebdomadaire.",
    "Renforcer la documentation et le partage de connaissances.",
    "Monter en compétence sur les rituels de feedback.",
    "Améliorer la gestion du temps sur les projets parallèles.",
    "Développer la prise de parole en public.",
    "Consolider les compétences techniques transverses.",
]

for emp in employees:
    hire = date.fromisoformat(emp["hire_date"])
    for period in review_periods:
        year = int(period.split("-")[0])
        semester = int(period.split("S")[1])
        review_date = date(year, 6, 30) if semester == 1 else date(year, 12, 31)
        if review_date < hire or review_date > TODAY:
            continue

        performance_reviews.append({
            "id": f"perf-review-{emp['id']}-{period}",
            "employee_id": emp["id"],
            "review_period": period,
            "reviewer_name": "Manager direct" if emp["department_id"] != department_by_name["Ressources Humaines"] else "Pulse RH",
            "overall_score": round(random.uniform(2.8, 5.0), 1),
            "strengths": random.choice(strength_options),
            "improvement_areas": random.choice(improvement_options),
            "summary": "Revue de performance semestrielle.",
            "reviewed_at": datetime_str(datetime(review_date.year, review_date.month, random.randint(1, 28), tzinfo=timezone.utc)),
        })

with open("data_imports/15_performance_reviews.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "review_period", "reviewer_name", "overall_score", "strengths", "improvement_areas", "summary", "reviewed_at"])
    writer.writeheader()
    for row in performance_reviews:
        writer.writerow(row)

print(f"  → {len(performance_reviews)} revues de performance")

# ---------------------------------------------------------
# 14. Performance Objectives (current + historical)
# ---------------------------------------------------------
print("[14/21] Objectifs de performance...")
performance_objectives = []

objective_titles = [
    "Structurer un plan de progression métier",
    "Monter en expertise sur le périmètre équipe",
    "Fluidifier les rituels de collaboration",
    "Partager les connaissances sur les projets actifs",
    "Consolider les indicateurs de qualité de livraison",
    "Sécuriser les bonnes pratiques sécurité et RGPD",
    "Améliorer la satisfaction client interne",
    "Réduire le temps de cycle sur les livrables",
]

for emp in employees:
    hire = date.fromisoformat(emp["hire_date"])

    # Past completed objectives
    num_past = random.randint(1, 4)
    for pi in range(num_past):
        created = random_date(max(hire, COMPANY_START), TODAY - timedelta(days=90))
        performance_objectives.append({
            "id": f"perf-obj-{emp['id']}-past-{pi}",
            "employee_id": emp["id"],
            "title": random.choice(objective_titles),
            "description": "Objectif passé complété.",
            "status": "completed",
            "progress_pct": 100,
            "due_date": date_str(created + timedelta(days=random.randint(30, 180))),
            "created_at": datetime_str(datetime.combine(created, datetime.min.time(), tzinfo=timezone.utc)),
        })

    # Current objectives
    for ci in range(2):
        status = random.choice(["planned", "in_progress", "in_progress", "blocked"])
        performance_objectives.append({
            "id": f"perf-obj-{emp['id']}-current-{ci}",
            "employee_id": emp["id"],
            "title": random.choice(objective_titles),
            "description": "Objectif en cours du semestre.",
            "status": status,
            "progress_pct": random.randint(10, 85),
            "due_date": date_str(TODAY + timedelta(days=random.randint(20, 150))),
            "created_at": datetime_str(datetime.now(timezone.utc) - timedelta(days=random.randint(10, 90))),
        })

with open("data_imports/16_performance_objectives.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "title", "description", "status", "progress_pct", "due_date", "created_at"])
    writer.writeheader()
    for row in performance_objectives:
        writer.writerow(row)

print(f"  → {len(performance_objectives)} objectifs")

# ---------------------------------------------------------
# 15. Benefit Plans
# ---------------------------------------------------------
print("[15/21] Plans avantages...")
benefit_plans = [
    {"id": "benefit-health", "name": "Mutuelle Pulse Santé", "provider": "Harmonie Pulse", "category": "Santé", "coverage_summary": "Couverture santé famille, téléconsultation et prévention.", "enrollment_month": 10, "is_active": "true"},
    {"id": "benefit-mobility", "name": "Plan Mobilité Durable", "provider": "Pulse Mobility", "category": "Mobilité", "coverage_summary": "Transport, vélo et indemnités mobilité douce.", "enrollment_month": 9, "is_active": "true"},
    {"id": "benefit-retirement", "name": "Plan Épargne Retraite", "provider": "Pulse Invest", "category": "Retraite", "coverage_summary": "PER collectif avec abondement employeur.", "enrollment_month": 1, "is_active": "true"},
]

with open("data_imports/17_benefit_plans.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "provider", "category", "coverage_summary", "enrollment_month", "is_active"])
    writer.writeheader()
    for row in benefit_plans:
        writer.writerow(row)

# ---------------------------------------------------------
# 16. Employee Benefits
# ---------------------------------------------------------
print("[16/21] Avantages employés...")
employee_benefits = []

for emp in employees:
    for bp in benefit_plans:
        employee_benefits.append({
            "id": f"benefit-{emp['id']}-{bp['id'].split('-')[1]}",
            "employee_id": emp["id"],
            "benefit_plan_id": bp["id"],
            "status": "active" if emp["status"] == "actif" else "eligible",
            "effective_date": emp["hire_date"],
            "renewal_date": date_str(date(TODAY.year, bp["enrollment_month"], 1)),
            "tier_label": "Premium" if emp["status"] == "actif" else "Standard",
            "employer_contribution": random.choice([420, 960, 1800, 2400]),
            "notes": f"Plan {bp['name']} collaborateur.",
        })

with open("data_imports/18_employee_benefits.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "benefit_plan_id", "status", "effective_date", "renewal_date", "tier_label", "employer_contribution", "notes"])
    writer.writeheader()
    for row in employee_benefits:
        writer.writerow(row)

print(f"  → {len(employee_benefits)} rattachements avantages")

# ---------------------------------------------------------
# 17. Career Paths
# ---------------------------------------------------------
print("[17/21] Parcours de carrière...")
career_paths = []

for emp in employees:
    title_lookup = next((job["title"] for job in jobs if job["id"] == emp["job_id"]), "Collaborateur")
    target = f"Lead {title_lookup}" if "Lead" not in title_lookup and "Directeur" not in title_lookup else title_lookup

    career_paths.append({
        "id": f"career-path-{emp['id']}",
        "employee_id": emp["id"],
        "target_job_id": emp["job_id"],
        "target_title": target,
        "readiness_level": random.choice(["emerging", "ready_soon", "ready_now"]),
        "next_step": random.choice([
            "Renforcer la visibilité des réalisations trimestrielles.",
            "Finaliser la formation prioritaire et élargir le périmètre projet.",
            "Préparer une prise de responsabilité progressive sur l'équipe.",
            "Obtenir une certification dans le domaine cible.",
        ]),
        "mentor_name": "Pulse RH" if emp["department_id"] == department_by_name["Ressources Humaines"] else "Manager direct",
        "last_reviewed_at": datetime_str(datetime.now(timezone.utc) - timedelta(days=random.randint(7, 60))),
    })

with open("data_imports/19_career_paths.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "target_job_id", "target_title", "readiness_level", "next_step", "mentor_name", "last_reviewed_at"])
    writer.writeheader()
    for row in career_paths:
        writer.writerow(row)

print(f"  → {len(career_paths)} parcours")

# ---------------------------------------------------------
# 18. Mobility Requests
# ---------------------------------------------------------
print("[18/21] Demandes de mobilité...")
mobility_requests = []

# Demo mobility
mobility_requests.append({
    "id": "mobility-youssef-001",
    "employee_id": demo_employee_by_email["youssef.benali@pulse.ma"]["id"],
    "target_department_id": department_by_name["IT & Engineering"],
    "target_job_id": demo_employee_by_email["youssef.benali@pulse.ma"]["job_id"],
    "request_type": "skill_growth",
    "status": "submitted",
    "rationale": "Souhaite élargir son périmètre frontend et expérience collaborateur.",
    "requested_at": datetime_str(datetime.now(timezone.utc) - timedelta(days=12)),
    "reviewed_at": "",
})

# Random mobility requests (~15% of employees)
for emp in employees:
    if random.random() > 0.85:
        target_dep = random.choice(dep_ids)
        target_job = random.choice(dep_to_jobs[target_dep])
        req_status = random.choice(["draft", "submitted", "reviewed", "approved", "rejected"])
        requested_at = datetime.now(timezone.utc) - timedelta(days=random.randint(10, 300))
        reviewed_at = datetime_str(requested_at + timedelta(days=random.randint(5, 30))) if req_status in ("reviewed", "approved", "rejected") else ""

        mobility_requests.append({
            "id": gen_id(),
            "employee_id": emp["id"],
            "target_department_id": target_dep,
            "target_job_id": target_job,
            "request_type": random.choice(["internal_move", "skill_growth", "promotion_track"]),
            "status": req_status,
            "rationale": random.choice([
                "Souhait d'évolution vers un nouveau périmètre.",
                "Envie de développer de nouvelles compétences.",
                "Rapprochement géographique avec une autre équipe.",
                "Intérêt pour un projet stratégique dans ce département.",
            ]),
            "requested_at": datetime_str(requested_at),
            "reviewed_at": reviewed_at,
        })

with open("data_imports/20_mobility_requests.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "target_department_id", "target_job_id", "request_type", "status", "rationale", "requested_at", "reviewed_at"])
    writer.writeheader()
    for row in mobility_requests:
        writer.writerow(row)

print(f"  → {len(mobility_requests)} demandes de mobilité")

# ---------------------------------------------------------
# 19. Promotion History
# ---------------------------------------------------------
print("[19/21] Historique de promotions...")
promotion_history = []

# Demo promotions
for demo in DEMO_USERS:
    eid = demo_employee_by_email[demo["email"]]["id"]
    if demo["email"] in {"fatima.alaoui@pulse.ma", "karim.tazi@pulse.ma"}:
        current_title = next((job["title"] for job in jobs if job["id"] == demo_employee_by_email[demo["email"]]["job_id"]), "Collaborateur")
        promotion_history.append({
            "id": f"promotion-{eid}",
            "employee_id": eid,
            "previous_job_title": "Lead Engineer" if demo["email"] == "fatima.alaoui@pulse.ma" else "HR Business Partner",
            "new_job_title": current_title,
            "effective_date": date_str(TODAY - timedelta(days=220)),
            "notes": "Évolution de poste validée par la direction.",
        })

# Random promotions (~15-20% of employees with >2 years tenure)
for emp in employees:
    hire = date.fromisoformat(emp["hire_date"])
    tenure_days = (TODAY - hire).days
    if tenure_days > 730 and random.random() > 0.78:
        job_obj = next((j for j in jobs if j["id"] == emp["job_id"]), None)
        prev_title = random.choice(["Analyste", "Consultant Junior", "Assistant", "Stagiaire", "Chargé de mission"])
        promotion_history.append({
            "id": gen_id(),
            "employee_id": emp["id"],
            "previous_job_title": prev_title,
            "new_job_title": job_obj["title"] if job_obj else "Collaborateur",
            "effective_date": date_str(random_date(hire + timedelta(days=365), TODAY - timedelta(days=30))),
            "notes": random.choice([
                "Promotion suite à l'évaluation annuelle.",
                "Évolution naturelle dans le parcours de carrière.",
                "Prise de responsabilité élargie.",
                "Reconnaissance de la montée en compétence.",
            ]),
        })

with open("data_imports/21_promotion_history.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "previous_job_title", "new_job_title", "effective_date", "notes"])
    writer.writeheader()
    for row in promotion_history:
        writer.writerow(row)

print(f"  → {len(promotion_history)} promotions")

# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------
print("\n" + "=" * 60)
print("Génération terminée ! Résumé :")
print(f"  01_departments.csv      : {len(departments)} départements")
print(f"  02_jobs.csv             : {len(jobs)} postes")
print(f"  03_employees.csv        : {len(employees)} employés")
print(f"  04_contracts.csv        : {len(contracts)} contrats")
print(f"  05_leaves.csv           : {len(leaves)} congés")
print(f"  06_projects.csv         : {len(projects)} projets")
print(f"  07_tasks.csv            : {len(tasks)} tâches")
print(f"  08_attendances.csv      : {len(attendances)} présences")
print(f"  09_skills.csv           : {len(skills)} compétences")
print(f"  10_employee_skills.csv  : {len(employee_skills)} compétences employés")
print(f"  11_training_courses.csv : {len(training_courses)} formations")
print(f"  12_training_enrollments : {len(training_enrollments)} inscriptions")
print(f"  13_project_assignments  : {len(project_assignments)} affectations")
print(f"  14_engagement_snapshots : {len(engagement_snapshots)} snapshots")
print(f"  15_performance_reviews  : {len(performance_reviews)} revues")
print(f"  16_performance_objectives: {len(performance_objectives)} objectifs")
print(f"  17_benefit_plans.csv    : {len(benefit_plans)} plans")
print(f"  18_employee_benefits    : {len(employee_benefits)} rattachements")
print(f"  19_career_paths.csv     : {len(career_paths)} parcours")
print(f"  20_mobility_requests    : {len(mobility_requests)} demandes")
print(f"  21_promotion_history    : {len(promotion_history)} promotions")
print("=" * 60)
print("Fichiers sauvegardés dans 'data_imports/'")

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

# Ensure the output directory exists
os.makedirs("data_imports", exist_ok=True)

# Helper for date string
def get_random_date(start_years_ago=5, end_years_ago=0):
    start = datetime.now() - timedelta(days=365 * start_years_ago)
    end = datetime.now() - timedelta(days=365 * end_years_ago)
    return fake.date_between(start_date=start, end_date=end).isoformat()

# Number of entities
NUM_EMPLOYEES = 89

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
        "hire_date": demo["hire_date"].isoformat(),
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

for i in range(1, NUM_EMPLOYEES + 1):
    emp_id = f"emp-{i}"
    moroccan_first_names = ["Amine", "Youssef", "Mehdi", "Hamza", "Karim", "Oussama", "Ayoub", "Walid", "Anas", "Omar", "Fatima", "Salma", "Imane", "Hajar", "Meryem", "Sara", "Khaoula", "Kenza", "Nada", "Zineb", "Ilias", "Nizar", "Rachid", "Tariq", "Hicham"]
    moroccan_last_names = ["Alaoui", "Benali", "Chraibi", "Berrada", "Tazi", "Bennani", "El Fassi", "Guessous", "Lahlou", "El Idrissi", "Mansouri", "Tahiri", "Amrani", "El Malki", "Daoudi", "Ait", "Bouzid", "El Amrani", "Zerouali"]
    first_name = random.choice(moroccan_first_names)
    last_name = random.choice(moroccan_last_names)
    
    # Create email
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

non_demo_employees = [employee for employee in employees if not employee["id"].startswith("emp-demo-")]
fatima_id = demo_employee_by_email["fatima.alaoui@pulse.ma"]["id"]
sara_id = demo_employee_by_email["sara.bennani@pulse.ma"]["id"]
it_dep_id = department_by_name["IT & Engineering"]
for member in non_demo_employees[:6]:
    member["department_id"] = it_dep_id
    member["manager_id"] = fatima_id
for member in non_demo_employees[6:9]:
    member["manager_id"] = sara_id

# Update department managers now that we have employees
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

with open("data_imports/03_employees.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "user_id", "first_name", "last_name", "email", "phone", "hire_date", "status", "department_id", "job_id", "manager_id"])
    writer.writeheader()
    for e in employees:
        writer.writerow(e)

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

for demo in DEMO_USERS:
    row = demo_employee_by_email[demo["email"]]
    contracts = [
        contract
        for contract in contracts
        if not (contract["employee_id"] == row["id"] and contract["is_active"] == "true")
    ]
    contracts.append({
        "id": f"contract-{row['id']}",
        "employee_id": row["id"],
        "contract_type": demo["contract_type"],
        "start_date": demo["hire_date"].isoformat(),
        "end_date": "",
        "salary": demo["salary"],
        "is_active": "true",
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

leaves.append({
    "id": "leave-demo-youssef",
    "employee_id": demo_employee_by_email["youssef.benali@pulse.ma"]["id"],
    "start_date": (datetime.now().date() + timedelta(days=15)).isoformat(),
    "end_date": (datetime.now().date() + timedelta(days=17)).isoformat(),
    "leave_type": "Congés Payés",
    "status": "En attente",
    "reason": "Vacances d'été",
})

with open("data_imports/05_leaves.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "start_date", "end_date", "leave_type", "status", "reason"])
    writer.writeheader()
    for leave in leaves:
        writer.writerow(leave)

# ---------------------------------------------------------
# 6. Projects & Tasks
# ---------------------------------------------------------
print("Generating 06_projects_and_tasks.csv")
projects = []
tasks = []

projects.append({
    "id": "proj-demo-onboarding",
    "name": "Onboarding Demo",
    "description": "Projet support pour les tâches de démo et l'intégration collaborateur.",
    "start_date": (datetime.now().date() - timedelta(days=7)).isoformat(),
    "deadline": (datetime.now().date() + timedelta(days=30)).isoformat(),
    "status": "En cours",
    "priority": "Haute",
    "business_domain": "People Operations",
    "required_skill_ids": "skill-onboarding,skill-communication,skill-security",
    "manager_id": demo_employee_by_email["fatima.alaoui@pulse.ma"]["id"],
})
tasks.extend([
    {
        "id": "task-demo-setup",
        "project_id": "proj-demo-onboarding",
        "assignee_id": demo_employee_by_email["youssef.benali@pulse.ma"]["id"],
        "title": "Configurer le poste de travail",
        "description": "Installation des outils internes et accès.",
        "status": "À faire",
        "due_date": (datetime.now().date() + timedelta(days=2)).isoformat(),
        "evaluation_score": "",
    },
    {
        "id": "task-demo-manager-meeting",
        "project_id": "proj-demo-onboarding",
        "assignee_id": demo_employee_by_email["youssef.benali@pulse.ma"]["id"],
        "title": "Rencontre avec le manager",
        "description": "Point d'intégration avec Fatima Alaoui.",
        "status": "À faire",
        "due_date": (datetime.now().date() + timedelta(days=1)).isoformat(),
        "evaluation_score": "",
    },
])

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
        "status": status,
        "priority": random.choice(["Basse", "Moyenne", "Haute", "Critique"]),
        "business_domain": random.choice(["People Analytics", "Engineering", "Operations", "Finance", "Talent"]),
        "required_skill_ids": ",".join(random.sample(["skill-react", "skill-python", "skill-management", "skill-security", "skill-communication", "skill-data"], k=2)),
        "manager_id": random.choice(employees)["id"],
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
    writer = csv.DictWriter(f, fieldnames=["id", "name", "description", "start_date", "deadline", "status", "priority", "business_domain", "required_skill_ids", "manager_id"])
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

# ---------------------------------------------------------
# 8. Skills, Trainings, Assignments, Engagement
# ---------------------------------------------------------
print("Generating 09-14 advanced HR datasets")

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

skill_ids = [skill["id"] for skill in skills]
employee_skills = []
project_assignments = []
engagement_snapshots = []
performance_reviews = []
performance_objectives = []
benefit_plans = [
    {
        "id": "benefit-health",
        "name": "Mutuelle Pulse Santé",
        "provider": "Harmonie Pulse",
        "category": "Santé",
        "coverage_summary": "Couverture santé famille, téléconsultation et prévention.",
        "enrollment_month": 10,
        "is_active": "true",
    },
    {
        "id": "benefit-mobility",
        "name": "Plan Mobilité Durable",
        "provider": "Pulse Mobility",
        "category": "Mobilité",
        "coverage_summary": "Transport, vélo et indemnités mobilité douce.",
        "enrollment_month": 9,
        "is_active": "true",
    },
]
employee_benefits = []
career_paths = []
mobility_requests = []
promotion_history = []
training_courses = [
    {
        "id": "training-rgpd",
        "title": "Parcours sécurité & RGPD",
        "provider": "Pulse Academy",
        "duration_hours": 3,
        "level": "Foundation",
        "format": "e-learning",
        "description": "Formation obligatoire sur la sécurité et la confidentialité.",
        "target_skill_id": "skill-security",
        "required_for_job_family": "",
        "difficulty": "Foundation",
        "delivery_mode": "e-learning",
        "mandatory_for_roles": "collaborator,manager,hr,director,admin",
    },
    {
        "id": "training-react",
        "title": "React avancé",
        "provider": "Pulse Academy",
        "duration_hours": 6,
        "level": "Advanced",
        "format": "blended",
        "description": "Perfectionnement React orienté produit.",
        "target_skill_id": "skill-react",
        "required_for_job_family": "Software Engineer",
        "difficulty": "Advanced",
        "delivery_mode": "blended",
        "mandatory_for_roles": "",
    },
    {
        "id": "training-manager-101",
        "title": "Manager 101",
        "provider": "People Ops",
        "duration_hours": 4,
        "level": "Intermediate",
        "format": "présentiel",
        "description": "Fondamentaux du management de proximité.",
        "target_skill_id": "skill-management",
        "required_for_job_family": "Engineering Manager",
        "difficulty": "Intermediate",
        "delivery_mode": "présentiel",
        "mandatory_for_roles": "manager",
    },
    {
        "id": "training-onboarding",
        "title": "Concevoir un onboarding impactant",
        "provider": "People Ops",
        "duration_hours": 5,
        "level": "Intermediate",
        "format": "e-learning",
        "description": "Structurer un onboarding personnalisé et mesurable.",
        "target_skill_id": "skill-onboarding",
        "required_for_job_family": "Responsable RH",
        "difficulty": "Intermediate",
        "delivery_mode": "e-learning",
        "mandatory_for_roles": "hr",
    },
]

training_enrollments = []

project_ids = [project["id"] for project in projects]
for index, employee in enumerate(employees, start=1):
    if employee["job_id"] in {job_id_by_title.get("Software Engineer"), job_id_by_title.get("Développeur Frontend"), job_id_by_title.get("Développeur Backend")}:
        selected_skills = ["skill-react", "skill-python", "skill-security"]
    elif employee["job_id"] == job_id_by_title.get("Engineering Manager"):
        selected_skills = ["skill-management", "skill-communication", "skill-security"]
    elif employee["department_id"] == department_by_name["Ressources Humaines"]:
        selected_skills = ["skill-onboarding", "skill-payroll", "skill-security"]
    else:
        selected_skills = random.sample(skill_ids, k=3)

    for skill_index, skill_id in enumerate(selected_skills):
        employee_skills.append({
            "id": f"employee-skill-{employee['id']}-{skill_index + 1}",
            "employee_id": employee["id"],
            "skill_id": skill_id,
            "proficiency_level": random.choice(["beginner", "intermediate", "advanced", "expert"]),
            "years_experience": round(random.uniform(0.5, 8.0), 1),
            "is_primary": "true" if skill_index == 0 else "false",
            "last_assessed_at": (datetime.now() - timedelta(days=random.randint(15, 220))).isoformat(),
            "source": "import_seed",
            "validated_by": "Pulse RH",
            "validated_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(5, 90))).isoformat(),
            "last_used_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 45))).isoformat(),
            "confidence_score": random.randint(72, 98),
        })

    assigned_project_ids = random.sample(project_ids, k=2 if employee["status"] == "actif" else 1)
    for assignment_index, project_id in enumerate(assigned_project_ids):
        project_assignments.append({
            "id": f"assignment-{employee['id']}-{assignment_index + 1}",
            "project_id": project_id,
            "employee_id": employee["id"],
            "role_on_project": "Contributeur" if assignment_index else "Référent",
            "allocation_pct": 60 if assignment_index == 0 else 30,
            "start_date": (datetime.now().date() - timedelta(days=random.randint(10, 120))).isoformat(),
            "end_date": "",
            "is_active": "true",
        })

    base_score = 68
    if employee["department_id"] == department_by_name["IT & Engineering"]:
        base_score += 6
    if employee["status"] != "actif":
        base_score -= 14
    if employee["id"] == demo_employee_by_email["youssef.benali@pulse.ma"]["id"]:
        base_score = 84
    elif employee["id"] == demo_employee_by_email["fatima.alaoui@pulse.ma"]["id"]:
        base_score = 79
    elif employee["id"] == demo_employee_by_email["karim.tazi@pulse.ma"]["id"]:
        base_score = 82

    for pulse_index in range(3):
        pulse_score = max(42, min(96, base_score + random.randint(-6, 6) - pulse_index))
        trend = random.choice([-4, -2, 0, 2, 4]) if pulse_index < 2 else random.choice([-2, 0, 2])
        risk_band = "high" if pulse_score < 58 else "medium" if pulse_score < 74 else "low"
        engagement_snapshots.append({
            "id": f"engagement-{employee['id']}-{pulse_index + 1}",
            "employee_id": employee["id"],
            "score": pulse_score,
            "source": "pulse",
            "pulse_label": random.choice(["stable", "engaged", "watch", "boost"]),
            "comment": "Mesure générée pour alimenter les dashboards prédictifs.",
            "trend": trend,
            "risk_band": risk_band,
            "source_signals": json.dumps({
                "absences_30j": random.randint(0, 2 if employee["status"] == "actif" else 4),
                "overdue_tasks": random.randint(0, 3),
                "mandatory_training_gap": random.randint(0, 1),
                "active_projects": random.randint(1, 3),
            }, ensure_ascii=False),
            "captured_at": (datetime.now(timezone.utc) - timedelta(days=15 * pulse_index + random.randint(1, 4))).isoformat(),
        })

    performance_reviews.append({
        "id": f"performance-review-{employee['id']}",
        "employee_id": employee["id"],
        "review_period": "2026-S1",
        "reviewer_name": "Pulse RH" if employee["department_id"] == department_by_name["Ressources Humaines"] else "Manager direct",
        "overall_score": round(random.uniform(3.2, 4.8), 1),
        "strengths": random.choice([
            "Bonne autonomie et collaboration transverse.",
            "Excellente capacité d'exécution sur les sujets prioritaires.",
            "Communication claire et fiable avec l'équipe.",
        ]),
        "improvement_areas": random.choice([
            "Structurer davantage la priorisation hebdomadaire.",
            "Renforcer la documentation et le partage de connaissances.",
            "Monter en compétence sur les rituels de feedback.",
        ]),
        "summary": "Revue de performance générée pour alimenter les parcours de développement.",
        "reviewed_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(5, 45))).isoformat(),
    })

    performance_objectives.append({
        "id": f"performance-objective-{employee['id']}-1",
        "employee_id": employee["id"],
        "title": random.choice([
            "Structurer un plan de progression métier",
            "Monter en expertise sur le périmètre équipe",
            "Fluidifier les rituels de collaboration",
        ]),
        "description": "Objectif principal du semestre pour soutenir la progression individuelle.",
        "status": random.choice(["in_progress", "in_progress", "completed"]),
        "progress_pct": random.randint(35, 92),
        "due_date": (datetime.now().date() + timedelta(days=random.randint(20, 120))).isoformat(),
        "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(30, 90))).isoformat(),
    })
    performance_objectives.append({
        "id": f"performance-objective-{employee['id']}-2",
        "employee_id": employee["id"],
        "title": random.choice([
            "Partager les connaissances sur les projets actifs",
            "Consolider les indicateurs de qualité de livraison",
            "Sécuriser les bonnes pratiques sécurité et RGPD",
        ]),
        "description": "Objectif complémentaire aligné sur le contexte projet et les attendus du poste.",
        "status": random.choice(["planned", "in_progress", "blocked"]),
        "progress_pct": random.randint(10, 68),
        "due_date": (datetime.now().date() + timedelta(days=random.randint(45, 160))).isoformat(),
        "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(10, 70))).isoformat(),
    })

    employee_benefits.append({
        "id": f"benefit-{employee['id']}-health",
        "employee_id": employee["id"],
        "benefit_plan_id": "benefit-health",
        "status": "active" if employee["status"] == "actif" else "eligible",
        "effective_date": employee["hire_date"],
        "renewal_date": date(datetime.now().year, 10, 1).isoformat(),
        "tier_label": "Premium" if employee["status"] == "actif" else "Standard",
        "employer_contribution": 1800,
        "notes": "Plan santé principal collaborateur.",
    })
    employee_benefits.append({
        "id": f"benefit-{employee['id']}-mobility",
        "employee_id": employee["id"],
        "benefit_plan_id": "benefit-mobility",
        "status": "active" if employee["status"] == "actif" else "eligible",
        "effective_date": employee["hire_date"],
        "renewal_date": date(datetime.now().year, 9, 1).isoformat(),
        "tier_label": "Transport",
        "employer_contribution": 420,
        "notes": "Plan mobilité interne.",
    })

    title_lookup = next((job["title"] for job in jobs if job["id"] == employee["job_id"]), "Collaborateur")
    career_paths.append({
        "id": f"career-path-{employee['id']}",
        "employee_id": employee["id"],
        "target_job_id": employee["job_id"],
        "target_title": f"Lead {title_lookup}" if "Lead" not in title_lookup and "Directeur" not in title_lookup else title_lookup,
        "readiness_level": random.choice(["emerging", "ready_soon", "ready_now"]),
        "next_step": random.choice([
            "Renforcer la visibilité des réalisations trimestrielles.",
            "Finaliser la formation prioritaire et élargir le périmètre projet.",
            "Préparer une prise de responsabilité progressive sur l'équipe.",
        ]),
        "mentor_name": "Pulse RH" if employee["department_id"] == department_by_name["Ressources Humaines"] else "Manager direct",
        "last_reviewed_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(7, 45))).isoformat(),
    })

    training_enrollments.append({
        "id": f"training-enrollment-rgpd-{employee['id']}",
        "employee_id": employee["id"],
        "training_id": "training-rgpd",
        "status": "completed" if employee["status"] == "actif" and random.random() > 0.2 else "assigned",
        "assigned_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat(),
        "due_date": (datetime.now().date() + timedelta(days=20)).isoformat(),
        "completed_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 20))).isoformat() if employee["status"] == "actif" and random.random() > 0.2 else "",
        "score": random.randint(72, 98) if employee["status"] == "actif" and random.random() > 0.2 else "",
        "mandatory": "true",
        "assigned_by": "Pulse RH",
        "recommendation_reason": "Parcours de conformité obligatoire",
    })

for demo in DEMO_USERS:
    employee_id = demo_employee_by_email[demo["email"]]["id"]
    if demo["email"] == "youssef.benali@pulse.ma":
        training_enrollments.append({
            "id": "training-enrollment-youssef-react",
            "employee_id": employee_id,
            "training_id": "training-react",
            "status": "in_progress",
            "assigned_at": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
            "due_date": (datetime.now().date() + timedelta(days=14)).isoformat(),
            "completed_at": "",
            "score": "",
            "mandatory": "false",
            "assigned_by": "Fatima Alaoui",
            "recommendation_reason": "Projet frontend actif et montée en compétence produit",
        })
    if demo["email"] == "fatima.alaoui@pulse.ma":
        training_enrollments.append({
            "id": "training-enrollment-fatima-manager",
            "employee_id": employee_id,
            "training_id": "training-manager-101",
            "status": "completed",
            "assigned_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
            "due_date": (datetime.now().date() - timedelta(days=5)).isoformat(),
            "completed_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
            "score": 91,
            "mandatory": "true",
            "assigned_by": "Karim Tazi",
            "recommendation_reason": "Prise de poste managériale",
        })
    if demo["email"] == "karim.tazi@pulse.ma":
        training_enrollments.append({
            "id": "training-enrollment-karim-onboarding",
            "employee_id": employee_id,
            "training_id": "training-onboarding",
            "status": "completed",
            "assigned_at": (datetime.now(timezone.utc) - timedelta(days=28)).isoformat(),
            "due_date": (datetime.now().date() - timedelta(days=2)).isoformat(),
            "completed_at": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
            "score": 95,
            "mandatory": "true",
            "assigned_by": "Karim Tazi",
            "recommendation_reason": "Montée en compétence RH sur les parcours d'intégration",
        })
    if demo["email"] == "youssef.benali@pulse.ma":
        mobility_requests.append({
            "id": "mobility-youssef-001",
            "employee_id": employee_id,
            "target_department_id": department_by_name["IT & Engineering"],
            "target_job_id": demo_employee_by_email["youssef.benali@pulse.ma"]["job_id"],
            "request_type": "skill_growth",
            "status": "submitted",
            "rationale": "Souhaite élargir son périmètre frontend et expérience collaborateur.",
            "requested_at": (datetime.now(timezone.utc) - timedelta(days=12)).isoformat(),
            "reviewed_at": "",
        })
    if demo["email"] in {"fatima.alaoui@pulse.ma", "karim.tazi@pulse.ma"}:
        current_title = next((job["title"] for job in jobs if job["id"] == demo_employee_by_email[demo["email"]]["job_id"]), "Collaborateur")
        promotion_history.append({
            "id": f"promotion-{employee_id}",
            "employee_id": employee_id,
            "previous_job_title": "Lead Engineer" if demo["email"] == "fatima.alaoui@pulse.ma" else "HR Business Partner",
            "new_job_title": current_title,
            "effective_date": (datetime.now().date() - timedelta(days=220)).isoformat(),
            "notes": "Évolution seedée pour démontrer les parcours de carrière.",
        })

with open("data_imports/09_skills.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "category", "description", "level_scale", "is_certifiable", "is_active"])
    writer.writeheader()
    for row in skills:
        writer.writerow(row)

with open("data_imports/10_employee_skills.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "skill_id", "proficiency_level", "years_experience", "is_primary", "last_assessed_at", "source", "validated_by", "validated_at", "last_used_at", "confidence_score"])
    writer.writeheader()
    for row in employee_skills:
        writer.writerow(row)

with open("data_imports/11_training_courses.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "title", "provider", "duration_hours", "level", "format", "description", "target_skill_id", "required_for_job_family", "difficulty", "delivery_mode", "mandatory_for_roles"])
    writer.writeheader()
    for row in training_courses:
        writer.writerow(row)

with open("data_imports/12_training_enrollments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "training_id", "status", "assigned_at", "due_date", "completed_at", "score", "mandatory", "assigned_by", "recommendation_reason"])
    writer.writeheader()
    for row in training_enrollments:
        writer.writerow(row)

with open("data_imports/13_project_assignments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "project_id", "employee_id", "role_on_project", "allocation_pct", "start_date", "end_date", "is_active"])
    writer.writeheader()
    for row in project_assignments:
        writer.writerow(row)

with open("data_imports/14_engagement_snapshots.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "score", "source", "pulse_label", "comment", "trend", "risk_band", "source_signals", "captured_at"])
    writer.writeheader()
    for row in engagement_snapshots:
        writer.writerow(row)

with open("data_imports/15_performance_reviews.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "review_period", "reviewer_name", "overall_score", "strengths", "improvement_areas", "summary", "reviewed_at"])
    writer.writeheader()
    for row in performance_reviews:
        writer.writerow(row)

with open("data_imports/16_performance_objectives.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "title", "description", "status", "progress_pct", "due_date", "created_at"])
    writer.writeheader()
    for row in performance_objectives:
        writer.writerow(row)

with open("data_imports/17_benefit_plans.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "provider", "category", "coverage_summary", "enrollment_month", "is_active"])
    writer.writeheader()
    for row in benefit_plans:
        writer.writerow(row)

with open("data_imports/18_employee_benefits.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "benefit_plan_id", "status", "effective_date", "renewal_date", "tier_label", "employer_contribution", "notes"])
    writer.writeheader()
    for row in employee_benefits:
        writer.writerow(row)

with open("data_imports/19_career_paths.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "target_job_id", "target_title", "readiness_level", "next_step", "mentor_name", "last_reviewed_at"])
    writer.writeheader()
    for row in career_paths:
        writer.writerow(row)

with open("data_imports/20_mobility_requests.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "target_department_id", "target_job_id", "request_type", "status", "rationale", "requested_at", "reviewed_at"])
    writer.writeheader()
    for row in mobility_requests:
        writer.writerow(row)

with open("data_imports/21_promotion_history.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "previous_job_title", "new_job_title", "effective_date", "notes"])
    writer.writeheader()
    for row in promotion_history:
        writer.writerow(row)

print("Advanced HR datasets generation complete!")

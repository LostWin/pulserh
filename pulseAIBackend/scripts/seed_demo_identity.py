import asyncio
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.domain import (
    Contract, Department, Employee, Interview, Job, Leave, Project, Task, Workflow, WorkflowStep,
    Skill, EmployeeSkill, TrainingCourse, TrainingEnrollment, ProjectAssignment, EngagementSnapshot,
    EngagementEvent, PerformanceObjective, PerformanceReview, BenefitPlan, EmployeeBenefit,
    CareerPath, MobilityRequest, PromotionHistory,
)
from app.services.employee_identity_service import sync_employee_identity
try:
    from scripts.demo_identity_data import DEMO_USERS
except ModuleNotFoundError:
    from demo_identity_data import DEMO_USERS


async def get_or_create_department(db, name: str) -> Department:
    result = await db.execute(select(Department).filter(Department.name == name))
    department = result.scalar_one_or_none()
    if department:
        return department
    department = Department(name=name)
    db.add(department)
    await db.flush()
    return department


async def get_or_create_job(db, title: str) -> Job:
    result = await db.execute(select(Job).filter(Job.title == title))
    job = result.scalar_one_or_none()
    if job:
        return job
    job = Job(title=title, description=f"Poste seedé pour {title}")
    db.add(job)
    await db.flush()
    return job


async def get_or_create_employee(db, payload: dict) -> Employee:
    result = await db.execute(select(Employee).filter(Employee.email == payload["email"]))
    employee = result.scalar_one_or_none()
    if not employee:
        employee = Employee(email=payload["email"], first_name=payload["first_name"], last_name=payload["last_name"])
        db.add(employee)
        await db.flush()
    employee.first_name = payload["first_name"]
    employee.last_name = payload["last_name"]
    employee.status = payload["status"]
    employee.hire_date = payload["hire_date"]
    department = await get_or_create_department(db, payload["department"])
    job = await get_or_create_job(db, payload["job_title"])
    employee.department_id = department.id
    employee.job_id = job.id
    return employee


async def ensure_contract(db, employee: Employee, contract_type: str, salary: float):
    result = await db.execute(select(Contract).filter(Contract.employee_id == employee.id, Contract.is_active.is_(True)))
    contract = result.scalar_one_or_none()
    if not contract:
        contract = Contract(
            employee_id=employee.id,
            contract_type=contract_type,
            start_date=employee.hire_date,
            salary=salary,
            is_active=True,
        )
        db.add(contract)
    else:
        contract.contract_type = contract_type
        contract.salary = salary


async def ensure_leave(db, employee: Employee):
    result = await db.execute(select(Leave).filter(Leave.employee_id == employee.id))
    existing = result.scalars().all()
    if existing:
        return
    db.add(
        Leave(
            employee_id=employee.id,
            leave_type="Congés Payés",
            start_date=date.today() + timedelta(days=15),
            end_date=date.today() + timedelta(days=17),
            status="En attente",
            reason="Vacances d'été",
        )
    )


async def ensure_tasks(db, employee: Employee, manager: Employee | None):
    project_result = await db.execute(select(Project).filter(Project.name == "Onboarding Demo"))
    project = project_result.scalar_one_or_none()
    if not project:
        project = Project(name="Onboarding Demo", description="Projet support pour les tâches de démo", status="En cours")
        db.add(project)
        await db.flush()

    result = await db.execute(select(Task).filter(Task.assignee_id == employee.id))
    if result.scalars().first():
        return
    db.add_all(
        [
            Task(
                project_id=project.id,
                assignee_id=employee.id,
                title="Configurer le poste de travail",
                description="Installation des outils internes et accès.",
                status="À faire",
                due_date=date.today() + timedelta(days=2),
            ),
            Task(
                project_id=project.id,
                assignee_id=employee.id,
                title="Rencontre avec le manager",
                description=f"Point d'intégration avec {manager.first_name} {manager.last_name}" if manager else "Point d'intégration",
                status="À faire",
                due_date=date.today() + timedelta(days=1),
            ),
        ]
    )


async def ensure_workflow(db, employee: Employee):
    result = await db.execute(select(Workflow).filter(Workflow.employee_id == employee.id, Workflow.type == "onboarding"))
    workflow = result.scalar_one_or_none()
    if not workflow:
        workflow = Workflow(employee_id=employee.id, type="onboarding", status="running", progress_percent=35)
        db.add(workflow)
        await db.flush()
    step_result = await db.execute(select(WorkflowStep).filter(WorkflowStep.workflow_id == workflow.id))
    if step_result.scalars().first():
        return
    db.add_all(
        [
            WorkflowStep(workflow_id=workflow.id, name="Compléter le profil", description="Ajouter téléphone et adresse.", status="pending", sequence=1),
            WorkflowStep(workflow_id=workflow.id, name="Signer le contrat électronique", description="Validation RH requise.", status="pending", sequence=2),
            WorkflowStep(workflow_id=workflow.id, name="Formation sécurité & RGPD", description="Module e-learning obligatoire.", status="pending", sequence=3),
        ]
    )


async def ensure_manager_team(db, manager: Employee):
    result = await db.execute(
        select(Employee)
        .filter(Employee.department_id == manager.department_id, Employee.id != manager.id)
        .limit(5)
    )
    team = result.scalars().all()
    if len(team) < 5:
        result = await db.execute(select(Employee).filter(Employee.id != manager.id).limit(5))
        team = result.scalars().all()
    for member in team:
        member.manager_id = manager.id
        member.department_id = manager.department_id


async def ensure_interviews(db, manager: Employee):
    result = await db.execute(select(Employee).filter(Employee.manager_id == manager.id).limit(3))
    team = result.scalars().all()
    for idx, member in enumerate(team):
        exists = await db.execute(
            select(Interview).filter(Interview.employee_id == member.id, Interview.manager_id == manager.id)
        )
        if exists.scalar_one_or_none():
            continue
        db.add(
            Interview(
                employee_id=member.id,
                manager_id=manager.id,
                title="Entretien de suivi",
                interview_type="one_on_one",
                scheduled_at=datetime.now(timezone.utc) + timedelta(days=7 + idx * 5),
                status="Complété" if idx == 0 else "Planifié" if idx != 1 else "À planifier",
                location="Salle Horizon",
                notes="Préparation du point de suivi trimestriel.",
                duration_minutes=45,
                outcome="aligné" if idx == 0 else None,
                summary="Très bon alignement sur les priorités, avec besoin de renforcer la visibilité des avancements." if idx == 0 else None,
                next_actions=["Partager un point hebdomadaire", "Finaliser la formation recommandée"] if idx == 0 else None,
            )
        )


async def ensure_skills_and_trainings(db, employee: Employee):
    skill_definitions = [
        ("Sécurité & RGPD", "Compliance"),
        ("Communication", "Soft Skills"),
        ("Management", "Leadership"),
        ("Python", "Engineering"),
        ("React", "Engineering"),
        ("Onboarding", "People"),
    ]
    skills = {}
    for name, category in skill_definitions:
        result = await db.execute(select(Skill).filter(Skill.name == name))
        skill = result.scalar_one_or_none()
        if not skill:
            skill = Skill(
                name=name,
                category=category,
                level_scale="beginner-intermediate-advanced-expert",
                is_certifiable=name in {"Sécurité & RGPD"},
                is_active=True,
            )
            db.add(skill)
            await db.flush()
        skills[name] = skill

    training_definitions = [
        ("Parcours sécurité & RGPD", skills["Sécurité & RGPD"].id, True),
        ("Manager 101", skills["Management"].id, True),
        ("Concevoir un onboarding impactant", skills["Onboarding"].id, True),
        ("React avancé", skills["React"].id, False),
    ]
    trainings = {}
    for title, target_skill_id, _mandatory in training_definitions:
        result = await db.execute(select(TrainingCourse).filter(TrainingCourse.title == title))
        training = result.scalar_one_or_none()
        if not training:
            training = TrainingCourse(
                title=title,
                target_skill_id=target_skill_id,
                provider="Pulse Academy",
                difficulty="Intermediate",
                delivery_mode="e-learning",
                mandatory_for_roles=["hr"] if "onboarding" in title.lower() else ["manager"] if "manager" in title.lower() else ["collaborator", "manager", "hr", "director", "admin"] if "rgpd" in title.lower() else [],
            )
            db.add(training)
            await db.flush()
        trainings[title] = training

    mapped_skills = ["Sécurité & RGPD", "Communication"]
    job_result = await db.execute(select(Job).filter(Job.id == employee.job_id))
    job = job_result.scalar_one_or_none()
    job_title = (job.title if job else "").lower()
    if "manager" in job_title:
        mapped_skills.append("Management")
    elif "rh" in job_title:
        mapped_skills.append("Onboarding")
    else:
        mapped_skills.extend(["Python", "React"])

    for index, skill_name in enumerate(mapped_skills):
        exists = await db.execute(
            select(EmployeeSkill).filter(EmployeeSkill.employee_id == employee.id, EmployeeSkill.skill_id == skills[skill_name].id)
        )
        if exists.scalar_one_or_none():
            continue
        db.add(
            EmployeeSkill(
                employee_id=employee.id,
                skill_id=skills[skill_name].id,
                proficiency_level="advanced" if index == 0 else "intermediate",
                years_experience=2 + index,
                is_primary=index == 0,
                last_assessed_at=datetime.now(timezone.utc) - timedelta(days=21),
                source="seed_demo_identity",
                validated_by="Pulse RH",
                validated_at=datetime.now(timezone.utc) - timedelta(days=14),
                last_used_at=datetime.now(timezone.utc) - timedelta(days=5),
                confidence_score=90 - (index * 6),
            )
        )

    rgpd_training = trainings["Parcours sécurité & RGPD"]
    enrollment_result = await db.execute(
        select(TrainingEnrollment).filter(TrainingEnrollment.employee_id == employee.id, TrainingEnrollment.training_id == rgpd_training.id)
    )
    if not enrollment_result.scalar_one_or_none():
        db.add(
            TrainingEnrollment(
                employee_id=employee.id,
                training_id=rgpd_training.id,
                status="completed" if employee.status == "actif" else "assigned",
                assigned_at=datetime.now(timezone.utc) - timedelta(days=30),
                due_date=date.today() + timedelta(days=15),
                completed_at=datetime.now(timezone.utc) - timedelta(days=5) if employee.status == "actif" else None,
                score=92 if employee.status == "actif" else None,
                mandatory=True,
                assigned_by="Pulse RH",
                recommendation_reason="Conformité sécurité et confidentialité",
            )
        )


async def ensure_project_assignment(db, employee: Employee):
    project_result = await db.execute(select(Project).filter(Project.name == "Onboarding Demo"))
    project = project_result.scalar_one_or_none()
    if not project:
        project = Project(
            name="Onboarding Demo",
            description="Projet support pour les tâches de démo",
            status="En cours",
            priority="Haute",
            business_domain="People Operations",
            required_skill_ids=[],
        )
        db.add(project)
        await db.flush()
    if not project.required_skill_ids:
        skill_result = await db.execute(select(Skill).filter(Skill.name.in_(["Onboarding", "Communication", "Sécurité & RGPD"])))
        project.required_skill_ids = [skill.id for skill in skill_result.scalars().all()]

    exists = await db.execute(
        select(ProjectAssignment).filter(ProjectAssignment.employee_id == employee.id, ProjectAssignment.project_id == project.id)
    )
    if exists.scalar_one_or_none():
        return
    job_result = await db.execute(select(Job).filter(Job.id == employee.job_id))
    job = job_result.scalar_one_or_none()
    job_title = (job.title if job else "").lower()
    db.add(
        ProjectAssignment(
            employee_id=employee.id,
            project_id=project.id,
            role_on_project="Référent" if "manager" in job_title else "Contributeur",
            allocation_pct=50,
            start_date=date.today() - timedelta(days=14),
            is_active=True,
        )
    )


async def ensure_engagement_snapshots(db, employee: Employee):
    result = await db.execute(select(EngagementSnapshot).filter(EngagementSnapshot.employee_id == employee.id))
    if result.scalars().first():
        return
    base_score = 80 if employee.status == "actif" else 55
    for offset in range(3):
        db.add(
            EngagementSnapshot(
                employee_id=employee.id,
                score=max(40, min(96, base_score - offset * 2)),
                source="pulse",
                pulse_label="engaged" if base_score >= 75 else "watch",
                comment="Snapshot de démonstration",
                trend=0 if offset == 0 else -2,
                risk_band="low" if base_score >= 75 else "medium",
                source_signals={"attendance": 82, "tasks": 76, "training": 88},
                captured_at=datetime.now(timezone.utc) - timedelta(days=15 * offset),
            )
        )


async def ensure_engagement_events(db, employee: Employee):
    result = await db.execute(select(EngagementEvent).filter(EngagementEvent.employee_id == employee.id))
    if result.scalars().first():
        return
    db.add_all(
        [
            EngagementEvent(
                employee_id=employee.id,
                event_type="training_completed",
                label="Formation obligatoire complétée",
                intensity=78,
                source="lms",
                payload={"training": "RGPD"},
                occurred_at=datetime.now(timezone.utc) - timedelta(days=6),
            ),
            EngagementEvent(
                employee_id=employee.id,
                event_type="project_assignment",
                label="Contribution sur projet actif",
                intensity=70,
                source="projects",
                payload={"allocation_pct": 50},
                occurred_at=datetime.now(timezone.utc) - timedelta(days=10),
            ),
        ]
    )


async def ensure_performance_data(db, employee: Employee, reviewer: Employee | None):
    review_result = await db.execute(select(PerformanceReview).filter(PerformanceReview.employee_id == employee.id))
    if not review_result.scalars().first():
        db.add(
            PerformanceReview(
                employee_id=employee.id,
                reviewer_id=reviewer.id if reviewer else None,
                review_type="quarterly",
                period_label="Q2 2026",
                score=4.2 if employee.status == "actif" else 3.2,
                summary="Performance solide avec des axes clairs de progression.",
                strengths=["Fiabilité", "Collaboration", "Exécution"],
                improvement_areas=["Priorisation", "Communication transverse"],
            )
        )

    objective_result = await db.execute(select(PerformanceObjective).filter(PerformanceObjective.employee_id == employee.id))
    if not objective_result.scalars().first():
        db.add_all(
            [
                PerformanceObjective(
                    employee_id=employee.id,
                    owner_id=reviewer.id if reviewer else None,
                    title="Monter en compétence sur le périmètre clé du poste",
                    description="Objectif de progression aligné avec le poste et les besoins de l'équipe.",
                    status="in_progress",
                    progress_pct=55 if employee.status == "actif" else 20,
                    target_date=date.today() + timedelta(days=60),
                ),
                PerformanceObjective(
                    employee_id=employee.id,
                    owner_id=reviewer.id if reviewer else None,
                    title="Renforcer la communication de suivi",
                    description="Partager des points d'avancement plus réguliers et actionnables.",
                    status="planned",
                    progress_pct=15 if employee.status == "actif" else 0,
                    target_date=date.today() + timedelta(days=90),
                ),
            ]
        )


async def ensure_benefits_and_career(db, employee: Employee, reviewer: Employee | None):
    plan_definitions = [
        ("Mutuelle Pulse Santé", "Santé", "Harmonie Pulse", "Couverture santé famille et téléconsultation.", 10),
        ("Plan Mobilité Durable", "Mobilité", "Pulse Mobility", "Forfait mobilité durable et abonnement transport.", 9),
    ]
    plans = {}
    for name, category, provider, coverage_summary, enrollment_month in plan_definitions:
        result = await db.execute(select(BenefitPlan).filter(BenefitPlan.name == name))
        plan = result.scalar_one_or_none()
        if not plan:
            plan = BenefitPlan(
                name=name,
                category=category,
                provider=provider,
                coverage_summary=coverage_summary,
                enrollment_month=enrollment_month,
                is_active=True,
            )
            db.add(plan)
            await db.flush()
        plans[name] = plan

    enrollment_result = await db.execute(select(EmployeeBenefit).filter(EmployeeBenefit.employee_id == employee.id))
    if not enrollment_result.scalars().first():
        db.add_all(
            [
                EmployeeBenefit(
                    employee_id=employee.id,
                    benefit_plan_id=plans["Mutuelle Pulse Santé"].id,
                    status="active" if employee.status == "actif" else "eligible",
                    effective_date=employee.hire_date,
                    renewal_date=date(date.today().year, 10, 1),
                    tier_label="Premium" if employee.status == "actif" else "Standard",
                    employer_contribution=1800.0,
                    notes="Couverture socle avec options famille.",
                ),
                EmployeeBenefit(
                    employee_id=employee.id,
                    benefit_plan_id=plans["Plan Mobilité Durable"].id,
                    status="active" if employee.status == "actif" else "eligible",
                    effective_date=employee.hire_date,
                    renewal_date=date(date.today().year, 9, 1),
                    tier_label="Transport",
                    employer_contribution=420.0,
                    notes="Prise en charge transport et mobilité douce.",
                ),
            ]
        )

    job_result = await db.execute(select(Job).filter(Job.id == employee.job_id))
    job = job_result.scalar_one_or_none()
    current_title = job.title if job else "Collaborateur"
    career_result = await db.execute(select(CareerPath).filter(CareerPath.employee_id == employee.id))
    if not career_result.scalars().first():
        target_title = "Lead " + current_title if "lead" not in current_title.lower() and "directeur" not in current_title.lower() else current_title
        db.add(
            CareerPath(
                employee_id=employee.id,
                target_job_id=employee.job_id,
                target_title=target_title,
                readiness_level="ready_soon" if employee.status == "actif" else "emerging",
                next_step="Finaliser la montée en compétence prioritaire et documenter les réalisations du semestre.",
                mentor_name=f"{reviewer.first_name} {reviewer.last_name}" if reviewer else "Pulse RH",
                last_reviewed_at=datetime.now(timezone.utc) - timedelta(days=12),
            )
        )

    mobility_result = await db.execute(select(MobilityRequest).filter(MobilityRequest.employee_id == employee.id))
    if not mobility_result.scalars().first() and employee.email == "youssef.benali@pulse.ma":
        target_department = await get_or_create_department(db, "IT & Engineering")
        db.add(
            MobilityRequest(
                employee_id=employee.id,
                target_department_id=target_department.id,
                target_job_id=employee.job_id,
                request_type="skill_growth",
                status="submitted",
                rationale="Souhaite élargir son périmètre produit sur les sujets frontend et expérience collaborateur.",
                reviewed_at=None,
            )
        )

    promotion_result = await db.execute(select(PromotionHistory).filter(PromotionHistory.employee_id == employee.id))
    if not promotion_result.scalars().first() and employee.email in {"fatima.alaoui@pulse.ma", "karim.tazi@pulse.ma"}:
        db.add(
            PromotionHistory(
                employee_id=employee.id,
                previous_job_title="HR Business Partner" if employee.email == "karim.tazi@pulse.ma" else "Lead Engineer",
                new_job_title=current_title,
                effective_date=date.today() - timedelta(days=220),
                notes="Évolution seedée pour donner du contexte carrière et mobilité.",
            )
        )


async def main():
    async with AsyncSessionLocal() as db:
        seeded = {}
        for payload in DEMO_USERS:
            employee = await get_or_create_employee(db, payload)
            seeded[payload["email"]] = employee
        await db.flush()

        for payload in DEMO_USERS:
            employee = seeded[payload["email"]]
            manager_email = payload["manager_email"]
            employee.manager_id = seeded[manager_email].id if manager_email and manager_email in seeded else None
            await ensure_contract(db, employee, payload["contract_type"], payload["salary"])
            await ensure_skills_and_trainings(db, employee)
            await ensure_project_assignment(db, employee)
            await ensure_engagement_snapshots(db, employee)
            await ensure_engagement_events(db, employee)
            reviewer = seeded.get(payload["manager_email"]) if payload["manager_email"] else None
            await ensure_performance_data(db, employee, reviewer)
            await ensure_benefits_and_career(db, employee, reviewer)
            if employee.email == "youssef.benali@pulse.ma":
                await ensure_leave(db, employee)
                await ensure_workflow(db, employee)

        await ensure_manager_team(db, seeded["fatima.alaoui@pulse.ma"])
        await ensure_tasks(db, seeded["youssef.benali@pulse.ma"], seeded["fatima.alaoui@pulse.ma"])
        await ensure_interviews(db, seeded["fatima.alaoui@pulse.ma"])
        await db.commit()

        for payload in DEMO_USERS:
            await sync_employee_identity(seeded[payload["email"]].id, db)

        print("Demo identity seed applied.")


if __name__ == "__main__":
    asyncio.run(main())

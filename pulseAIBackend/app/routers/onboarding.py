
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.rbac import require_collaborator
from app.database import get_db
from app.dependencies import get_current_user
from app.models.domain import Document, Employee, ProjectAssignment, TrainingEnrollment, Workflow
from app.routers.dashboard import _get_current_employee
from app.schemas.auth import CurrentUser
from app.schemas.onboarding import (
    OnboardingContact,
    OnboardingOverviewResponse,
    OnboardingPathStep,
    OnboardingResource,
    OnboardingStepResponse,
)

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.get("/me", response_model=OnboardingOverviewResponse, dependencies=[Depends(require_collaborator)])
async def get_my_onboarding(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    current_employee = await _get_current_employee(current_user, db)
    employee_result = await db.execute(
        select(Employee)
        .options(
            selectinload(Employee.contracts),
            selectinload(Employee.tasks),
            selectinload(Employee.manager).selectinload(Employee.job),
            selectinload(Employee.workflows).selectinload(Workflow.steps),
            selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
            selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
        )
        .where(Employee.id == current_employee.id)
    )
    employee = employee_result.scalar_one()
    documents_result = await db.execute(select(Document).order_by(Document.created_at.desc()).limit(10))
    documents = documents_result.scalars().all()

    workflow = next((item for item in employee.workflows if item.type == "onboarding"), None)
    workflow_steps = workflow.steps if workflow else []
    task_items = []
    for step in workflow_steps:
        task_items.append(
            OnboardingStepResponse(
                id=step.id,
                label=step.name,
                status=step.status,
                detail=step.description or "Étape préparée par l'équipe RH.",
                due_label=step.due_date.strftime("%d/%m/%Y") if step.due_date else None,
            )
        )

    if not task_items:
        task_items = []
        task_items.append(
            OnboardingStepResponse(
                id="profile",
                label="Compléter le profil",
                status="done" if employee.phone else "pending",
                detail="Renseignez vos informations personnelles et de contact.",
            )
        )
        task_items.append(
            OnboardingStepResponse(
                id="contract",
                label="Finaliser le dossier contractuel",
                status="done" if employee.contracts else "pending",
                detail="Le contrat et les pièces administratives doivent être validés dans le SI.",
            )
        )
        mandatory_training = next((enrollment for enrollment in employee.training_enrollments if enrollment.mandatory and enrollment.status != "completed"), None)
        task_items.append(
            OnboardingStepResponse(
                id="security",
                label="Compléter les formations prioritaires",
                status="done" if mandatory_training is None else "pending",
                detail=(
                    f"Terminer la formation '{mandatory_training.training.title}'." if mandatory_training and mandatory_training.training
                    else "Aucune formation obligatoire restante."
                ),
            )
        )
        if employee.manager:
            task_items.append(
                OnboardingStepResponse(
                    id="manager",
                    label="Planifier le point manager",
                    status="done" if any(step.status == "done" and "manager" in step.name.lower() for step in workflow_steps) else "pending",
                    detail=f"Prévoir un premier tête-à-tête avec {employee.manager.first_name} {employee.manager.last_name}.",
                )
            )

    path = [
        OnboardingPathStep(id="profile", label="Profile Setup", status="done" if employee.phone else "pending"),
        OnboardingPathStep(id="contract", label="Contract Signing", status="done" if employee.contracts else "pending"),
        OnboardingPathStep(id="it", label="IT Setup", status="done" if employee.tasks else "pending"),
        OnboardingPathStep(id="team", label="Team Intro", status="done" if employee.manager else "pending"),
    ]
    completed_steps = sum(1 for step in path if step.status == "done")
    progress_percent = round((completed_steps / len(path)) * 100)

    contacts = []
    if employee.manager:
        contacts.append(
            OnboardingContact(
                name=f"{employee.manager.first_name} {employee.manager.last_name}",
                role=employee.manager.job.title if employee.manager.job else "Manager",
                initials=f"{employee.manager.first_name[:1]}{employee.manager.last_name[:1]}".upper(),
                color="#1F524B",
                main=True,
            )
        )
    contacts.append(OnboardingContact(name="Support RH", role="Ressources humaines", initials="RH", color="#DF4931"))

    resources = []
    for document in documents[:3]:
        resources.append(OnboardingResource(label=document.name, type="document"))
    for enrollment in employee.training_enrollments[:3]:
        if enrollment.training:
            resources.append(OnboardingResource(label=f"Formation · {enrollment.training.title}", type="training"))
    for assignment in employee.project_assignments[:2]:
        if assignment.project:
            resources.append(OnboardingResource(label=f"Projet d'équipe · {assignment.project.name}", type="project"))

    if not resources:
        if employee.manager:
            resources.append(OnboardingResource(label=f"Contact manager · {employee.manager.first_name} {employee.manager.last_name}", type="directory"))
        if employee.job:
            resources.append(OnboardingResource(label=f"Parcours métier · {employee.job.title}", type="training"))
        if not resources:
            resources.append(OnboardingResource(label="Annuaire d'équipe", type="directory"))

    return OnboardingOverviewResponse(
        progress_percent=progress_percent,
        completed_steps=completed_steps,
        total_steps=len(path),
        title=f"Welcome to the Team, {employee.first_name}!",
        subtitle="Votre parcours d'intégration est maintenant piloté par les workflows et données réelles.",
        path=path,
        tasks=task_items,
        resources=resources[:6],
        contacts=contacts,
    )

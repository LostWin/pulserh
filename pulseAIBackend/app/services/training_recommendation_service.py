from __future__ import annotations

from typing import Iterable

from app.models.domain import Employee, Skill, TrainingCourse
from app.schemas.talent import TrainingRecommendationItem
from app.services.role_mapping_service import infer_access_role_for_employee


def _normalize_job_family(job_title: str | None) -> str:
    if not job_title:
        return ""
    return job_title.strip().lower()


def recommend_trainings_for_employee(
    employee: Employee,
    trainings: Iterable[TrainingCourse],
    skills_by_id: dict[str, Skill],
) -> list[TrainingRecommendationItem]:
    employee_skill_ids = {item.skill_id for item in employee.skills}
    active_project_skill_ids: set[str] = set()
    for assignment in employee.project_assignments:
        if assignment.is_active and assignment.project and assignment.project.required_skill_ids:
            active_project_skill_ids.update(assignment.project.required_skill_ids)

    enrolled_training_ids = {item.training_id for item in employee.training_enrollments}
    current_roles = {infer_access_role_for_employee(employee)}
    job_family = _normalize_job_family(employee.job.title if employee.job else None)

    recommendations: list[TrainingRecommendationItem] = []
    for training in trainings:
        if training.id in enrolled_training_ids:
            continue

        reasons: list[str] = []
        score = 35
        mandatory = False

        if training.target_skill_id and training.target_skill_id not in employee_skill_ids:
            skill_name = skills_by_id.get(training.target_skill_id).name if training.target_skill_id in skills_by_id else "compétence cible"
            reasons.append(f"Compétence à développer: {skill_name}")
            score += 28

        if training.target_skill_id and training.target_skill_id in active_project_skill_ids:
            skill_name = skills_by_id.get(training.target_skill_id).name if training.target_skill_id in skills_by_id else "compétence projet"
            reasons.append(f"Projet d'équipe actif lié à {skill_name}")
            score += 22

        if training.required_for_job_family and job_family and training.required_for_job_family.lower() in job_family:
            reasons.append(f"Alignée avec le poste {employee.job.title if employee.job else ''}".strip())
            score += 16

        mandatory_roles = set(training.mandatory_for_roles or [])
        if mandatory_roles and current_roles & mandatory_roles:
            reasons.append("Obligatoire pour votre rôle")
            score += 30
            mandatory = True

        if not reasons and training.target_skill_id in employee_skill_ids:
            reasons.append("Renforcement recommandé sur une compétence existante")
            score += 8

        if reasons:
            recommendations.append(
                TrainingRecommendationItem(
                    training_id=training.id,
                    title=training.title,
                    provider=training.provider,
                    target_skill_name=skills_by_id.get(training.target_skill_id).name if training.target_skill_id in skills_by_id else None,
                    relevance_score=min(100, score),
                    reasons=reasons,
                    mandatory=mandatory,
                )
            )

    recommendations.sort(key=lambda item: (item.mandatory, item.relevance_score), reverse=True)
    return recommendations[:8]

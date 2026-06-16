from io import BytesIO
from pathlib import Path
import textwrap
import zipfile

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.import_service import process_csv_import
from app.dependencies import get_current_user

# Models
from app.models.domain import (
    Department, Job, Employee, Contract, Leave, Project, Task, Attendance,
    Skill, EmployeeSkill, TrainingCourse, TrainingEnrollment, ProjectAssignment, EngagementSnapshot,
    PerformanceReview, PerformanceObjective, BenefitPlan, EmployeeBenefit, CareerPath, MobilityRequest, PromotionHistory,
)

# Schemas
from app.schemas.import_schemas import (
    DepartmentImport, JobImport, EmployeeImport, ContractImport, 
    LeaveImport, ProjectImport, TaskImport, AttendanceImport, ImportHistoryResponse,
    SkillImport, EmployeeSkillImport, TrainingCourseImport, TrainingEnrollmentImport,
    ProjectAssignmentImport, EngagementSnapshotImport, PerformanceReviewImport, PerformanceObjectiveImport,
    BenefitPlanImport, EmployeeBenefitImport, CareerPathImport, MobilityRequestImport, PromotionHistoryImport,
)
from app.schemas.employee import ImportReport

router = APIRouter(
    prefix="/imports",
    tags=["Imports"]
)

SAMPLE_FILES_DIR = Path(__file__).resolve().parents[2] / "data_imports"

SAMPLE_FILE_DESCRIPTIONS = {
    "01_departments.csv": "Référentiel des départements. À importer en premier pour créer les rattachements organisationnels.",
    "02_jobs.csv": "Référentiel des postes. À importer avant les employés pour permettre le rattachement job_id.",
    "03_employees.csv": "Base collaborateurs. Dépend des départements et des postes via department_id et job_id.",
    "04_contracts.csv": "Contrats salariés. Dépend des employés via employee_id.",
    "05_leaves.csv": "Congés et absences. Dépend des employés via employee_id.",
    "06_projects.csv": "Catalogue des projets. Doit être présent avant les tâches.",
    "07_tasks.csv": "Tâches projets. Dépend des projets via project_id et optionnellement des employés via assignee_id.",
    "08_attendances.csv": "Présences quotidiennes. Dépend des employés via employee_id.",
    "09_skills.csv": "Référentiel de compétences. À importer avant les compétences collaborateur et les formations ciblées.",
    "10_employee_skills.csv": "Compétences par collaborateur. Dépend des employés et des compétences.",
    "11_training_courses.csv": "Catalogue de formations. Peut cibler une compétence et une famille de postes.",
    "12_training_enrollments.csv": "Affectations et complétions de formation. Dépend des employés et des formations.",
    "13_project_assignments.csv": "Affectations collaborateurs/projets. Dépend des projets et des employés.",
    "14_engagement_snapshots.csv": "Photographies d'engagement ou pulse surveys. Dépend des employés.",
    "15_performance_reviews.csv": "Revues de performance par collaborateur. Dépend des employés.",
    "16_performance_objectives.csv": "Objectifs de performance et de progression. Dépend des employés.",
    "17_benefit_plans.csv": "Catalogue des avantages salariés. À importer avant les rattachements collaborateur.",
    "18_employee_benefits.csv": "Rattachements collaborateurs/benefits. Dépend des employés et des plans benefit.",
    "19_career_paths.csv": "Cibles carrière individuelles. Dépend des employés et optionnellement des jobs.",
    "20_mobility_requests.csv": "Demandes de mobilité interne. Dépend des employés, départements et jobs cibles.",
    "21_promotion_history.csv": "Historique d'évolution de poste. Dépend des employés.",
}

SAMPLE_SCHEMA_DETAILS = {
    "departments": [
        ("id", "string", "oui", "Identifiant unique stable du département."),
        ("name", "string", "oui", "Nom lisible du département."),
        ("manager_id", "string", "non", "Référence vers employee.id du manager du département."),
    ],
    "jobs": [
        ("id", "string", "oui", "Identifiant unique stable du poste."),
        ("title", "string", "oui", "Intitulé du poste."),
        ("level", "string", "non", "Niveau du poste: Junior, Mid, Senior, Executive, etc."),
        ("description", "string", "non", "Description libre du poste."),
    ],
    "employees": [
        ("id", "string", "oui", "Identifiant unique stable du collaborateur."),
        ("user_id", "string", "non", "Identifiant SSO/Keycloak si déjà connu."),
        ("first_name", "string", "oui", "Prénom."),
        ("last_name", "string", "oui", "Nom de famille."),
        ("email", "email", "oui", "Adresse email valide et unique côté métier."),
        ("phone", "string", "non", "Téléphone libre."),
        ("hire_date", "date YYYY-MM-DD", "oui", "Date d'embauche."),
        ("status", "string", "oui", "Statut RH, ex: actif."),
        ("department_id", "string", "non", "Référence vers departments.id."),
        ("job_id", "string", "non", "Référence vers jobs.id."),
        ("manager_id", "string", "non", "Référence vers employees.id d'un manager existant ou importé ensuite via réimport."),
    ],
    "contracts": [
        ("id", "string", "oui", "Identifiant unique stable du contrat."),
        ("employee_id", "string", "oui", "Référence vers employees.id."),
        ("contract_type", "string", "oui", "Type de contrat, ex: CDI, CDD."),
        ("start_date", "date YYYY-MM-DD", "oui", "Date de début du contrat."),
        ("end_date", "date YYYY-MM-DD", "non", "Date de fin si applicable."),
        ("salary", "number", "oui", "Salaire numérique sans séparateur de milliers."),
        ("is_active", "boolean", "oui", "true ou false."),
    ],
    "leaves": [
        ("id", "string", "oui", "Identifiant unique stable de la demande."),
        ("employee_id", "string", "oui", "Référence vers employees.id."),
        ("start_date", "date YYYY-MM-DD", "oui", "Début du congé."),
        ("end_date", "date YYYY-MM-DD", "oui", "Fin du congé."),
        ("leave_type", "string", "oui", "Type de congé."),
        ("status", "string", "oui", "Statut métier, ex: En attente, Approuvé."),
        ("reason", "string", "non", "Motif libre."),
    ],
    "projects": [
        ("id", "string", "oui", "Identifiant unique stable du projet."),
        ("name", "string", "oui", "Nom du projet."),
        ("description", "string", "non", "Description libre."),
        ("start_date", "date YYYY-MM-DD", "non", "Date de démarrage."),
        ("deadline", "date YYYY-MM-DD", "non", "Date cible."),
        ("status", "string", "oui", "Statut projet, ex: En cours, Terminé."),
        ("priority", "string", "non", "Priorité métier, ex: Haute, Critique."),
        ("business_domain", "string", "non", "Domaine métier du projet."),
        ("required_skill_ids", "string liste séparée par virgules", "non", "IDs de compétences attendues pour le projet."),
        ("manager_id", "string", "non", "Référence vers employees.id du référent projet."),
    ],
    "tasks": [
        ("id", "string", "oui", "Identifiant unique stable de la tâche."),
        ("project_id", "string", "oui", "Référence vers projects.id."),
        ("assignee_id", "string", "non", "Référence vers employees.id."),
        ("title", "string", "oui", "Titre de la tâche."),
        ("description", "string", "non", "Description libre."),
        ("status", "string", "oui", "Statut de la tâche."),
        ("due_date", "date YYYY-MM-DD", "non", "Échéance."),
        ("evaluation_score", "number", "non", "Score d'évaluation numérique."),
    ],
    "attendances": [
        ("id", "string", "oui", "Identifiant unique stable de la ligne de présence."),
        ("employee_id", "string", "oui", "Référence vers employees.id."),
        ("date", "date YYYY-MM-DD", "oui", "Jour de présence."),
        ("check_in", "datetime ISO-8601", "non", "Heure d'arrivée."),
        ("check_out", "datetime ISO-8601", "non", "Heure de départ."),
        ("status", "string", "oui", "Présent, Absent, Retard, etc."),
    ],
    "skills": [
        ("id", "string", "oui", "Identifiant unique stable de la compétence."),
        ("name", "string", "oui", "Nom de la compétence."),
        ("category", "string", "non", "Catégorie métier ou technique."),
        ("description", "string", "non", "Description libre."),
        ("level_scale", "string", "non", "Échelle de niveau attendue."),
        ("is_certifiable", "boolean", "oui", "true si la compétence peut être certifiée."),
        ("is_active", "boolean", "oui", "true si la compétence est active au catalogue."),
    ],
    "employee_skills": [
        ("id", "string", "oui", "Identifiant unique stable de la ligne."),
        ("employee_id", "string", "oui", "Référence vers employees.id."),
        ("skill_id", "string", "oui", "Référence vers skills.id."),
        ("proficiency_level", "string", "oui", "Niveau de maîtrise."),
        ("years_experience", "number", "non", "Années d'expérience approximatives."),
        ("is_primary", "boolean", "oui", "true si compétence principale."),
        ("last_assessed_at", "datetime ISO-8601", "non", "Date de dernière évaluation."),
        ("source", "string", "non", "Origine de la donnée: import, manager_review, auto, etc."),
        ("validated_by", "string", "non", "Nom du validateur si applicable."),
        ("validated_at", "datetime ISO-8601", "non", "Date de validation."),
        ("last_used_at", "datetime ISO-8601", "non", "Dernière utilisation observée."),
        ("confidence_score", "number (0-100)", "non", "Niveau de confiance sur la maîtrise."),
    ],
    "training_courses": [
        ("id", "string", "oui", "Identifiant unique stable de la formation."),
        ("title", "string", "oui", "Titre de la formation."),
        ("provider", "string", "non", "Organisme ou plateforme."),
        ("duration_hours", "number", "non", "Durée estimée en heures."),
        ("level", "string", "non", "Niveau de difficulté."),
        ("format", "string", "non", "Présentiel, e-learning, blended, etc."),
        ("description", "string", "non", "Description libre."),
        ("target_skill_id", "string", "non", "Référence vers skills.id si pertinent."),
        ("required_for_job_family", "string", "non", "Famille de poste concernée."),
        ("difficulty", "string", "non", "Niveau de difficulté métier."),
        ("delivery_mode", "string", "non", "Modalité de diffusion: e-learning, blended, présentiel."),
        ("mandatory_for_roles", "string liste séparée par virgules", "non", "Rôles pour lesquels la formation est obligatoire."),
    ],
    "training_enrollments": [
        ("id", "string", "oui", "Identifiant unique stable de l'inscription."),
        ("employee_id", "string", "oui", "Référence vers employees.id."),
        ("training_id", "string", "oui", "Référence vers training_courses.id."),
        ("status", "string", "oui", "assigned, in_progress, completed, overdue."),
        ("assigned_at", "datetime ISO-8601", "non", "Date d'affectation."),
        ("due_date", "date YYYY-MM-DD", "non", "Date d'échéance."),
        ("completed_at", "datetime ISO-8601", "non", "Date de complétion."),
        ("score", "number", "non", "Score obtenu si applicable."),
        ("mandatory", "boolean", "oui", "true si formation obligatoire."),
        ("assigned_by", "string", "non", "Personne ou service ayant affecté la formation."),
        ("recommendation_reason", "string", "non", "Raison métier de l'affectation."),
    ],
    "project_assignments": [
        ("id", "string", "oui", "Identifiant unique stable de l'affectation."),
        ("project_id", "string", "oui", "Référence vers projects.id."),
        ("employee_id", "string", "oui", "Référence vers employees.id."),
        ("role_on_project", "string", "non", "Rôle sur le projet."),
        ("allocation_pct", "number", "non", "Charge allouée en pourcentage."),
        ("start_date", "date YYYY-MM-DD", "non", "Début de l'affectation."),
        ("end_date", "date YYYY-MM-DD", "non", "Fin si connue."),
        ("is_active", "boolean", "oui", "true si l'affectation est active."),
    ],
    "engagement_snapshots": [
        ("id", "string", "oui", "Identifiant unique stable de la mesure."),
        ("employee_id", "string", "oui", "Référence vers employees.id."),
        ("score", "number (0-100)", "oui", "Score d'engagement."),
        ("source", "string", "oui", "Origine: survey, pulse, manager_review, etc."),
        ("pulse_label", "string", "non", "Libellé qualitatif éventuel."),
        ("comment", "string", "non", "Commentaire complémentaire."),
        ("trend", "number", "non", "Tendance calculée par rapport à la mesure précédente."),
        ("risk_band", "string", "non", "Niveau low/medium/high associé à la mesure."),
        ("source_signals", "JSON ou liste sérialisée", "non", "Résumé structuré des signaux contributeurs."),
        ("captured_at", "datetime ISO-8601", "non", "Date de la mesure."),
    ],
    "performance_reviews": [
        ("id", "string", "oui", "Identifiant unique stable de la revue."),
        ("employee_id", "string", "oui", "Référence vers employees.id."),
        ("review_period", "string", "oui", "Période de revue, ex: 2026-S1."),
        ("reviewer_name", "string", "non", "Nom du reviewer ou manager."),
        ("overall_score", "number", "non", "Score global de performance."),
        ("strengths", "string", "non", "Forces principales identifiées."),
        ("improvement_areas", "string", "non", "Axes de progression."),
        ("summary", "string", "non", "Synthèse rédigée de la revue."),
        ("reviewed_at", "datetime ISO-8601", "non", "Date effective de revue."),
    ],
    "performance_objectives": [
        ("id", "string", "oui", "Identifiant unique stable de l'objectif."),
        ("employee_id", "string", "oui", "Référence vers employees.id."),
        ("title", "string", "oui", "Titre de l'objectif."),
        ("description", "string", "non", "Description détaillée."),
        ("status", "string", "oui", "planned, in_progress, completed, blocked."),
        ("progress_pct", "number (0-100)", "oui", "Progression de l'objectif."),
        ("due_date", "date YYYY-MM-DD", "non", "Date cible."),
        ("created_at", "datetime ISO-8601", "non", "Date de création."),
    ],
    "benefit_plans": [
        ("id", "string", "oui", "Identifiant unique stable du plan."),
        ("name", "string", "oui", "Nom du plan benefit."),
        ("provider", "string", "non", "Prestataire ou assureur."),
        ("category", "string", "oui", "Santé, mobilité, retraite, etc."),
        ("coverage_summary", "string", "non", "Résumé de couverture."),
        ("enrollment_month", "number (1-12)", "non", "Mois de fenêtre d'adhésion."),
        ("is_active", "boolean", "oui", "Plan actif ou non."),
    ],
    "employee_benefits": [
        ("id", "string", "oui", "Identifiant unique stable du rattachement."),
        ("employee_id", "string", "oui", "Référence vers employees.id."),
        ("benefit_plan_id", "string", "oui", "Référence vers benefit_plans.id."),
        ("status", "string", "oui", "active, eligible, suspended, archived."),
        ("effective_date", "date YYYY-MM-DD", "non", "Date d'effet."),
        ("renewal_date", "date YYYY-MM-DD", "non", "Date de renouvellement."),
        ("tier_label", "string", "non", "Niveau ou pack couvert."),
        ("employer_contribution", "number", "non", "Contribution employeur annuelle."),
        ("notes", "string", "non", "Complément métier."),
    ],
    "career_paths": [
        ("id", "string", "oui", "Identifiant unique stable du parcours."),
        ("employee_id", "string", "oui", "Référence vers employees.id."),
        ("target_job_id", "string", "non", "Référence vers jobs.id."),
        ("target_title", "string", "oui", "Intitulé cible."),
        ("readiness_level", "string", "oui", "emerging, ready_soon, ready_now."),
        ("next_step", "string", "non", "Prochaine étape recommandée."),
        ("mentor_name", "string", "non", "Mentor ou sponsor suggéré."),
        ("last_reviewed_at", "datetime ISO-8601", "non", "Dernière revue de ce parcours."),
    ],
    "mobility_requests": [
        ("id", "string", "oui", "Identifiant unique stable de la demande."),
        ("employee_id", "string", "oui", "Référence vers employees.id."),
        ("target_department_id", "string", "non", "Référence vers departments.id."),
        ("target_job_id", "string", "non", "Référence vers jobs.id."),
        ("request_type", "string", "oui", "internal_move, skill_growth, promotion_track, etc."),
        ("status", "string", "oui", "draft, submitted, reviewed, approved, rejected."),
        ("rationale", "string", "non", "Motivation de la demande."),
        ("requested_at", "datetime ISO-8601", "non", "Date de demande."),
        ("reviewed_at", "datetime ISO-8601", "non", "Date de revue."),
    ],
    "promotion_history": [
        ("id", "string", "oui", "Identifiant unique stable de l'évolution."),
        ("employee_id", "string", "oui", "Référence vers employees.id."),
        ("previous_job_title", "string", "non", "Ancien intitulé."),
        ("new_job_title", "string", "oui", "Nouvel intitulé."),
        ("effective_date", "date YYYY-MM-DD", "oui", "Date d'effet."),
        ("notes", "string", "non", "Commentaire RH."),
    ],
}


def build_samples_memo() -> str:
    sections = [
        "# Kit d'import PulseAI",
        "",
        "Ce dossier contient des exemples prêts à l'emploi pour guider la préparation des imports CSV.",
        "",
        "## Ordre recommandé d'import",
        "1. `01_departments.csv`",
        "2. `02_jobs.csv`",
        "3. `03_employees.csv`",
        "4. `04_contracts.csv`",
        "5. `05_leaves.csv`",
        "6. `06_projects.csv`",
        "7. `07_tasks.csv`",
        "8. `08_attendances.csv`",
        "9. `09_skills.csv`",
        "10. `10_employee_skills.csv`",
        "11. `11_training_courses.csv`",
        "12. `12_training_enrollments.csv`",
        "13. `13_project_assignments.csv`",
        "14. `14_engagement_snapshots.csv`",
        "15. `15_performance_reviews.csv`",
        "16. `16_performance_objectives.csv`",
        "17. `17_benefit_plans.csv`",
        "18. `18_employee_benefits.csv`",
        "19. `19_career_paths.csv`",
        "20. `20_mobility_requests.csv`",
        "21. `21_promotion_history.csv`",
        "",
        "## Règles générales",
        "- Les en-têtes doivent rester exactement identiques.",
        "- Chaque ligne doit avoir un `id` stable et unique dans son entité.",
        "- Le moteur d'import fonctionne en upsert: un `id` existant met à jour la ligne, un `id` inconnu crée une nouvelle ligne.",
        "- Les références entre fichiers (`department_id`, `job_id`, `employee_id`, `project_id`, etc.) doivent pointer vers des identifiants déjà importés ou présents en base.",
        "- Utiliser les dates au format `YYYY-MM-DD`.",
        "- Utiliser les dates/horaires au format ISO-8601 pour les colonnes datetime.",
        "- Utiliser `true` / `false` pour les booléens.",
        "- Éviter de renommer, traduire ou réordonner les colonnes sans vérifier les schémas attendus.",
        "",
        "## Utilité de chaque fichier",
    ]

    for filename, description in SAMPLE_FILE_DESCRIPTIONS.items():
        sections.append(f"- `{filename}`: {description}")

    sections.extend(["", "## Détail des colonnes attendues"])

    for entity_name, fields in SAMPLE_SCHEMA_DETAILS.items():
        sections.extend(["", f"### {entity_name}"])
        sections.append("| Colonne | Type attendu | Obligatoire | Description |")
        sections.append("| --- | --- | --- | --- |")
        for column, data_type, required, description in fields:
            sections.append(f"| `{column}` | {data_type} | {required} | {description} |")

    sections.extend([
        "",
        "## Interdépendances à surveiller",
        "- `employees.department_id` doit exister dans `departments.id`.",
        "- `employees.job_id` doit exister dans `jobs.id`.",
        "- `employees.manager_id` et `departments.manager_id` doivent pointer vers un `employees.id` valide.",
        "- `contracts.employee_id`, `leaves.employee_id` et `attendances.employee_id` doivent pointer vers un `employees.id` valide.",
        "- `tasks.project_id` doit exister dans `projects.id`.",
        "- `tasks.assignee_id` doit pointer vers un `employees.id` valide quand il est renseigné.",
        "- `employee_skills.skill_id` doit exister dans `skills.id`.",
        "- `training_courses.target_skill_id` doit exister dans `skills.id` quand il est renseigné.",
        "- `training_enrollments.training_id` doit exister dans `training_courses.id`.",
        "- `project_assignments.project_id` et `project_assignments.employee_id` doivent pointer vers des IDs valides.",
        "- `engagement_snapshots.employee_id` doit pointer vers un `employees.id` valide.",
        "- `performance_reviews.employee_id` et `performance_objectives.employee_id` doivent pointer vers un `employees.id` valide.",
        "- `employee_benefits.benefit_plan_id` doit exister dans `benefit_plans.id`.",
        "- `career_paths.target_job_id` doit exister dans `jobs.id` s'il est renseigné.",
        "- `mobility_requests.target_department_id` et `mobility_requests.target_job_id` doivent pointer vers des IDs valides si renseignés.",
        "",
        "## Conseils d'exploitation",
        "- Commencer par un petit jeu de données pour valider le mapping.",
        "- Vérifier l'historique des imports après chaque chargement pour repérer les erreurs ligne par ligne.",
        "- En cas de dépendance circulaire manager/employé, importer d'abord les employés sans `manager_id`, puis faire un second import de mise à jour.",
    ])

    return textwrap.dedent("\n".join(sections)).strip() + "\n"

@router.get("/history", response_model=list[ImportHistoryResponse])
async def get_import_history(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    from sqlalchemy import select
    from app.models.domain import ImportHistory
    result = await db.execute(select(ImportHistory).order_by(ImportHistory.created_at.desc()))
    return result.scalars().all()


@router.get("/samples")
async def download_import_samples(current_user = Depends(get_current_user)):
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("README_IMPORT_SAMPLES.md", build_samples_memo())

        for sample_file in sorted(SAMPLE_FILES_DIR.glob("*.csv")):
            archive.write(sample_file, arcname=f"samples/{sample_file.name}")

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="pulseai-import-samples.zip"'},
    )

@router.post("/departments", response_model=ImportReport)
async def import_departments(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, DepartmentImport, Department, current_user.id, current_user.email, "departments")

@router.post("/jobs", response_model=ImportReport)
async def import_jobs(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, JobImport, Job, current_user.id, current_user.email, "jobs")

@router.post("/employees", response_model=ImportReport)
async def import_employees(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, EmployeeImport, Employee, current_user.id, current_user.email, "employees")

@router.post("/contracts", response_model=ImportReport)
async def import_contracts(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, ContractImport, Contract, current_user.id, current_user.email, "contracts")

@router.post("/leaves", response_model=ImportReport)
async def import_leaves(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, LeaveImport, Leave, current_user.id, current_user.email, "leaves")

@router.post("/projects", response_model=ImportReport)
async def import_projects(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, ProjectImport, Project, current_user.id, current_user.email, "projects")

@router.post("/tasks", response_model=ImportReport)
async def import_tasks(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, TaskImport, Task, current_user.id, current_user.email, "tasks")

@router.post("/attendances", response_model=ImportReport)
async def import_attendances(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, AttendanceImport, Attendance, current_user.id, current_user.email, "attendances")

@router.post("/skills", response_model=ImportReport)
async def import_skills(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, SkillImport, Skill, current_user.id, current_user.email, "skills")

@router.post("/employee-skills", response_model=ImportReport)
async def import_employee_skills(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, EmployeeSkillImport, EmployeeSkill, current_user.id, current_user.email, "employee_skills")

@router.post("/training-courses", response_model=ImportReport)
async def import_training_courses(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, TrainingCourseImport, TrainingCourse, current_user.id, current_user.email, "training_courses")

@router.post("/training-enrollments", response_model=ImportReport)
async def import_training_enrollments(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, TrainingEnrollmentImport, TrainingEnrollment, current_user.id, current_user.email, "training_enrollments")

@router.post("/project-assignments", response_model=ImportReport)
async def import_project_assignments(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, ProjectAssignmentImport, ProjectAssignment, current_user.id, current_user.email, "project_assignments")

@router.post("/engagement-snapshots", response_model=ImportReport)
async def import_engagement_snapshots(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, EngagementSnapshotImport, EngagementSnapshot, current_user.id, current_user.email, "engagement_snapshots")

@router.post("/performance-reviews", response_model=ImportReport)
async def import_performance_reviews(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, PerformanceReviewImport, PerformanceReview, current_user.id, current_user.email, "performance_reviews")

@router.post("/performance-objectives", response_model=ImportReport)
async def import_performance_objectives(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, PerformanceObjectiveImport, PerformanceObjective, current_user.id, current_user.email, "performance_objectives")

@router.post("/benefit-plans", response_model=ImportReport)
async def import_benefit_plans(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, BenefitPlanImport, BenefitPlan, current_user.id, current_user.email, "benefit_plans")

@router.post("/employee-benefits", response_model=ImportReport)
async def import_employee_benefits(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, EmployeeBenefitImport, EmployeeBenefit, current_user.id, current_user.email, "employee_benefits")

@router.post("/career-paths", response_model=ImportReport)
async def import_career_paths(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, CareerPathImport, CareerPath, current_user.id, current_user.email, "career_paths")

@router.post("/mobility-requests", response_model=ImportReport)
async def import_mobility_requests(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, MobilityRequestImport, MobilityRequest, current_user.id, current_user.email, "mobility_requests")

@router.post("/promotion-history", response_model=ImportReport)
async def import_promotion_history(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await process_csv_import(file, db, PromotionHistoryImport, PromotionHistory, current_user.id, current_user.email, "promotion_history")

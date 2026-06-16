"""
Outils IA (Tool-Calling) pour Pulse AI.

Chaque outil est une fonction async qui peut être appelée par le LLM 
via le mécanisme de function-calling d'OpenAI.

Ces outils permettent à l'IA de :
- Récupérer les données de l'employé connecté
- Consulter les soldes de congés
- Voir les contrats actifs
- Consulter les présences récentes
- Générer des documents RH
- Rechercher dans la base de connaissances
"""

import logging
import json
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.domain import (
    Employee, EmployeeSkill, Contract, Leave, Attendance, Task, Document,
    ProjectAssignment, TrainingCourse, TrainingEnrollment,
)
from app.services.calendar_connector import calendar_connector
from app.services.field_access_service import apply_field_access, get_primary_role
from app.services.hr_analytics_service import current_project_names

from app.services.ai_observability_service import ai_observability_service
from app.models.domain import Alert
from sqlalchemy import or_


logger = logging.getLogger("pulse.services.ai_tools")


def _format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} o"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} Ko"
    return f"{size_bytes / (1024 * 1024):.1f} Mo"


async def _get_employee(db: AsyncSession, user_id: str, *, options: list | None = None) -> Employee | None:
    query = select(Employee).filter((Employee.user_id == user_id) | (Employee.id == user_id))
    if options:
        query = query.options(*options)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def _apply_tool_access(
    db: AsyncSession,
    *,
    resource: str,
    scope: str,
    payload: dict,
    user_roles: list[str] | None,
    context: dict | None = None,
) -> dict:
    filtered, field_visibility = await apply_field_access(
        db,
        resource=resource,
        scope=scope,
        payload=payload,
        role=get_primary_role(user_roles or ["collaborator"]),
        context=context or {"is_self": True},
    )
    filtered["_field_visibility"] = field_visibility
    return filtered


# ════════════════════════════════════════════════════════════════
# Définition des outils au format OpenAI function-calling
# ════════════════════════════════════════════════════════════════

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_employee_info",
            "description": "Récupérer les informations du profil de l'employé connecté : nom, prénom, poste, département, date d'embauche, email, statut.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_leave_balance",
            "description": "Consulter le solde de congés de l'employé connecté : jours restants, jours pris, historique récent des demandes de congés.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_contracts",
            "description": "Récupérer les contrats actifs de l'employé connecté : type de contrat (CDI, CDD, etc.), salaire, dates de début et fin.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_attendances",
            "description": "Consulter l'historique de présence récent de l'employé connecté (30 derniers jours) : dates, heures d'arrivée/départ, statut.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_document",
            "description": "Générer un document RH officiel pour l'employé connecté. Types disponibles : attestation_travail, certificat_salaire, autorisation_teletravail.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_type": {
                        "type": "string",
                        "enum": ["attestation_travail", "certificat_salaire", "autorisation_teletravail"],
                        "description": "Le type de document à générer.",
                    },
                },
                "required": ["document_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_tasks",
            "description": "Récupérer la liste des tâches et projets assignés à l'employé connecté avec leur statut et évaluation.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recommend_trainings",
            "description": "Suggérer des formations utiles selon les compétences connues du collaborateur et les projets de son équipe.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_manager_availability",
            "description": "Proposer des créneaux plausibles de 1:1 avec le manager en se basant sur les entretiens déjà planifiés.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_one_on_one",
            "description": "Créer un entretien 1:1 avec le manager du collaborateur sur le prochain créneau disponible.",
            "parameters": {
                "type": "object",
                "properties": {
                    "days_from_now": {"type": "integer", "description": "Décalage en jours pour le rendez-vous souhaité.", "default": 5}
                },
                "required": [],
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "search_employee",
            "description": "Rechercher un employé par nom ou prénom pour trouver son ID. Utile pour les managers ou RH avant d'utiliser d'autres outils nécessitant un ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Nom ou prénom à rechercher."}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_employee_profile",
            "description": "Obtenir le profil complet d'un employé cible (via son ID). Renvoie ses informations de base selon les droits du demandeur (DAC).",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "L'ID de l'employé cible (uuid)."}
                },
                "required": ["employee_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_employee_contracts",
            "description": "Obtenir les contrats d'un employé cible (via son ID). Le salaire et autres champs sensibles seront filtrés si le demandeur n'a pas les droits.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "string", "description": "L'ID de l'employé cible (uuid)."}
                },
                "required": ["employee_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_team_alerts",
            "description": "Récupère les alertes en cours (absences, tâches en retard, etc.) pour l'équipe du manager qui pose la question.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


# ════════════════════════════════════════════════════════════════
# Implémentation des fonctions d'outils
# ════════════════════════════════════════════════════════════════

async def get_employee_info(db: AsyncSession, user_id: str, user_roles: list[str] | None = None, **kwargs) -> str:
    """Récupérer les infos du profil de l'employé connecté."""
    logger.info(f"Outil get_employee_info() appelé pour user_id={user_id}")
    
    query = select(Employee).options(
        selectinload(Employee.department),
        selectinload(Employee.job)
    ).filter(
        (Employee.user_id == user_id) | (Employee.id == user_id)
    )
    result = await db.execute(query)
    emp = result.scalar_one_or_none()
    
    if not emp:
        return json.dumps({"error": "Employé non trouvé"}, ensure_ascii=False)
    
    payload = {
        "id": emp.id,
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "email": emp.email,
        "phone": emp.phone,
        "hire_date": emp.hire_date.isoformat() if emp.hire_date else None,
        "status": emp.status,
        "department": emp.department.name if emp.department else "Non assigné",
        "job_title": emp.job.title if emp.job else "Non défini",
    }
    return json.dumps(
        await _apply_tool_access(
            db,
            resource="employee",
            scope="self",
            payload=payload,
            user_roles=user_roles,
        ),
        ensure_ascii=False,
    )


async def get_leave_balance(db: AsyncSession, user_id: str, user_roles: list[str] | None = None, **kwargs) -> str:
    """Consulter le solde de congés."""
    logger.info(f"Outil get_leave_balance() appelé pour user_id={user_id}")
    
    # Trouver l'employé
    emp = await _get_employee(db, user_id)
    
    if not emp:
        return json.dumps({"error": "Employé non trouvé"}, ensure_ascii=False)
    
    # Compter les congés de l'année en cours
    current_year = date.today().year
    leaves_query = select(Leave).filter(
        Leave.employee_id == emp.id,
        func.extract('year', Leave.start_date) == current_year
    )
    leaves_result = await db.execute(leaves_query)
    leaves = leaves_result.scalars().all()
    
    total_annual = 25  # Jours annuels standard
    days_taken = sum(
        (leave.end_date - leave.start_date).days + 1 
        for leave in leaves 
        if leave.status in ("Approuvé", "approved")
    )
    days_pending = sum(
        (leave.end_date - leave.start_date).days + 1 
        for leave in leaves 
        if leave.status in ("En attente", "pending")
    )
    
    recent_leaves = []
    for leave in sorted(leaves, key=lambda x: x.start_date, reverse=True)[:5]:
        recent_leaves.append(
            await _apply_tool_access(
                db,
                resource="leave",
                scope="request",
                payload={
                    "leave_type": leave.leave_type,
                    "start_date": leave.start_date.isoformat(),
                    "end_date": leave.end_date.isoformat(),
                    "status": leave.status,
                    "reason": leave.reason,
                },
                user_roles=user_roles,
            )
        )

    return json.dumps({
        "total_annual_days": total_annual,
        "days_taken": days_taken,
        "days_pending": days_pending,
        "days_remaining": total_annual - days_taken,
        "recent_leaves": recent_leaves,
    }, ensure_ascii=False)


async def get_contracts(db: AsyncSession, user_id: str, user_roles: list[str] | None = None, **kwargs) -> str:
    """Récupérer les contrats actifs."""
    logger.info(f"Outil get_contracts() appelé pour user_id={user_id}")
    
    emp = await _get_employee(db, user_id)
    
    if not emp:
        return json.dumps({"error": "Employé non trouvé"}, ensure_ascii=False)
    
    contracts_query = select(Contract).filter(Contract.employee_id == emp.id)
    contracts_result = await db.execute(contracts_query)
    contracts = contracts_result.scalars().all()
    
    contracts_payload = []
    for contract in contracts:
        contract_payload = await _apply_tool_access(
            db,
            resource="employee",
            scope="self",
            payload={
                "contract_type": contract.contract_type,
                "salary": contract.salary,
            },
            user_roles=user_roles,
        )
        contracts_payload.append(
            {
                "type": contract_payload.get("contract_type"),
                "start_date": contract.start_date.isoformat() if contract.start_date else None,
                "end_date": contract.end_date.isoformat() if contract.end_date else None,
                "salary": contract_payload.get("salary"),
                "is_active": contract.is_active,
                "_field_visibility": contract_payload.get("_field_visibility", {}),
            }
        )
    return json.dumps({"contracts": contracts_payload}, ensure_ascii=False)


async def get_recent_attendances(db: AsyncSession, user_id: str, user_roles: list[str] | None = None, **kwargs) -> str:
    """Historique de présence récent (30 derniers jours)."""
    logger.info(f"Outil get_recent_attendances() appelé pour user_id={user_id}")
    
    emp = await _get_employee(db, user_id)
    
    if not emp:
        return json.dumps({"error": "Employé non trouvé"}, ensure_ascii=False)
    
    thirty_days_ago = date.today() - timedelta(days=30)
    att_query = select(Attendance).filter(
        Attendance.employee_id == emp.id,
        Attendance.date >= thirty_days_ago
    ).order_by(Attendance.date.desc())
    att_result = await db.execute(att_query)
    attendances = att_result.scalars().all()
    
    return json.dumps({
        "attendances": [
            {
                "date": a.date.isoformat(),
                "check_in": a.check_in.isoformat() if a.check_in else None,
                "check_out": a.check_out.isoformat() if a.check_out else None,
                "status": a.status,
            }
            for a in attendances
        ],
        "summary": {
            "total_days": len(attendances),
            "present": sum(1 for a in attendances if a.status == "Présent"),
            "absent": sum(1 for a in attendances if a.status == "Absent"),
            "late": sum(1 for a in attendances if a.status == "Retard"),
        },
    }, ensure_ascii=False)


async def generate_document_tool(db: AsyncSession, user_id: str, user_roles: list[str] | None = None, document_type: str = "attestation_travail", **kwargs) -> str:
    """Générer un document RH dynamique via le DocumentGenerator."""
    logger.info(f"Outil generate_document() appelé | user_id={user_id}, type={document_type}")
    
    from app.services.document_generator import document_generator
    from app.services.secure_document_storage import secure_document_storage
    from app.models.domain import DocumentType
    
    doc_type_obj = (await db.execute(select(DocumentType).filter(DocumentType.code == document_type))).scalar_one_or_none()
    if not doc_type_obj:
        return json.dumps({"error": f"Type de document inconnu: {document_type}."}, ensure_ascii=False)
        
    if doc_type_obj.allowed_roles and len(doc_type_obj.allowed_roles) > 0:
        has_access = any(r in doc_type_obj.allowed_roles for r in user_roles) or "admin" in user_roles
        if not has_access:
            return json.dumps({"error": f"ACCES_REFUSE: Vos rôles ({', '.join(user_roles)}) ne sont pas autorisés à générer ce type de document."}, ensure_ascii=False)
    
    emp_query = select(Employee).options(
        selectinload(Employee.department),
        selectinload(Employee.job),
        selectinload(Employee.contracts),
        selectinload(Employee.leaves),
        selectinload(Employee.manager)
    ).filter(
        (Employee.user_id == user_id) | (Employee.id == user_id)
    )
    emp = (await db.execute(emp_query)).scalar_one_or_none()
    
    if not emp:
        return json.dumps({"error": "Employé non trouvé"}, ensure_ascii=False)
        
    contract_obj = emp.contracts[0] if emp.contracts else None
    
    # Construire la payload de base
    raw_payload = {
        "employee": {
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "email": emp.email,
            "phone": emp.phone,
            "address": emp.address if hasattr(emp, 'address') else "Adresse non renseignée",
            "hire_date": str(emp.hire_date) if emp.hire_date else ""
        },
        "contract": {
            "type": contract_obj.contract_type if contract_obj else "CDI",
            "start_date": str(contract_obj.start_date) if contract_obj and contract_obj.start_date else "",
            "end_date": str(contract_obj.end_date) if contract_obj and contract_obj.end_date else "",
            "salary": contract_obj.salary if contract_obj else 0,
            "status": "Actif" if contract_obj and getattr(contract_obj, "is_active", True) else "Inactif"
        },
        "job": {
            "title": emp.job.title if emp.job else "Poste non défini",
            "department": emp.department.name if emp.department else "Département non défini"
        },
        "manager": {
            "first_name": emp.manager.first_name if emp.manager else "",
            "last_name": emp.manager.last_name if emp.manager else "",
            "email": emp.manager.email if emp.manager else ""
        }
    }
    
    # Application du DAC sur tout l'employé
    filtered_payload = await _apply_tool_access(db, resource="employee", scope="self", payload=raw_payload, user_roles=user_roles)
    
    # Vérifier que les variables requises sont bien lisibles
    for req_var in doc_type_obj.required_variables:
        parts = req_var.split(".")
        if len(parts) == 2:
            group, key = parts
            group_visibility = filtered_payload.get("_field_visibility", {}).get(group, "visible")
            if isinstance(group_visibility, dict):
                visibility = group_visibility.get(key, "visible")
            else:
                visibility = group_visibility
                
            if visibility != "visible":
                return json.dumps({"error": f"ACCES_REFUSE: La variable '{req_var}' est requise pour générer ce document, mais vous n'avez pas les droits de la lire."}, ensure_ascii=False)
                
    # Extraire les objets filtrés pour le context Jinja2
    context = {
        "employee": filtered_payload.get("employee", raw_payload["employee"]),
        "contract": filtered_payload.get("contract", raw_payload["contract"]),
        "job": filtered_payload.get("job", raw_payload["job"]),
        "manager": filtered_payload.get("manager", raw_payload["manager"]),
        "salary_formatted": f"{raw_payload['contract']['salary']:,.2f}".replace(",", " "),
        "monthly_salary_formatted": f"{(raw_payload['contract']['salary'] / 12):,.2f}".replace(",", " ") if isinstance(raw_payload['contract']['salary'], (int, float)) else "N/A",
    }
    
    try:
        filename, pdf_bytes = await document_generator.create_pdf_bytes(db=db, doc_type_code=document_type, context=context)
        storage_uri = secure_document_storage.upload_bytes(pdf_bytes, filename, "generated")

        status = "pending" if doc_type_obj.responsible_role else "validated"
        
        db.add(Document(
            name=filename,
            type=document_type,
            size=_format_file_size(len(pdf_bytes)),
            file_path=storage_uri,
            uploaded_by=f"IA pour {emp.first_name} {emp.last_name}",
            allowed_roles=["collaborator", "hr", "admin"],
            status=status,
            employee_id=emp.id,
            document_type_id=doc_type_obj.id
        ))
        await db.commit()

        msg = f"Le document '{doc_type_obj.name}' a été généré avec succès."
        if status == "pending":
            msg += f" Il est actuellement en attente de validation par le service ({doc_type_obj.responsible_role})."
            
        return json.dumps({
            "success": True,
            "document_type": document_type,
            "file_name": filename,
            "status": status,
            "message": msg,
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erreur lors de la génération du document : {e}")
        return json.dumps({"error": f"Erreur lors de la génération : {str(e)}"}, ensure_ascii=False)


async def get_my_tasks(db: AsyncSession, user_id: str, user_roles: list[str] | None = None, **kwargs) -> str:
    """Récupérer les tâches et projets assignés."""
    logger.info(f"Outil get_my_tasks() appelé pour user_id={user_id}")
    
    emp = await _get_employee(db, user_id)
    
    if not emp:
        return json.dumps({"error": "Employé non trouvé"}, ensure_ascii=False)
    
    tasks_query = select(Task).options(
        selectinload(Task.project)
    ).filter(Task.assignee_id == emp.id)
    tasks_result = await db.execute(tasks_query)
    tasks = tasks_result.scalars().all()
    
    return json.dumps({
        "tasks": [
            {
                "title": t.title,
                "project": t.project.name if t.project else "Aucun",
                "status": t.status,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "evaluation_score": t.evaluation_score,
            }
            for t in tasks
        ],
        "summary": {
            "total": len(tasks),
            "todo": sum(1 for t in tasks if t.status == "À faire"),
            "in_progress": sum(1 for t in tasks if t.status == "En cours"),
            "done": sum(1 for t in tasks if t.status == "Terminé"),
        },
    }, ensure_ascii=False)


async def recommend_trainings(db: AsyncSession, user_id: str, user_roles: list[str] | None = None, **kwargs) -> str:
    logger.info(f"Outil recommend_trainings() appelé pour user_id={user_id}")
    emp = await _get_employee(
        db,
        user_id,
        options=[
            selectinload(Employee.skills).selectinload(EmployeeSkill.skill),
            selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
            selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
            selectinload(Employee.job),
        ],
    )
    if not emp:
        return json.dumps({"error": "Employé non trouvé"}, ensure_ascii=False)

    skill_ids = {item.skill_id for item in emp.skills}
    existing_training_ids = {item.training_id for item in emp.training_enrollments}
    trainings = (await db.execute(select(TrainingCourse))).scalars().all()
    recommendations = []
    for training in trainings:
        if training.id in existing_training_ids:
            continue
        matches_skill = training.target_skill_id and training.target_skill_id in skill_ids
        matches_job = training.required_for_job_family and emp.job and training.required_for_job_family.lower() in emp.job.title.lower()
        if matches_skill or matches_job:
            recommendations.append(
                {
                    "title": training.title,
                    "provider": training.provider,
                    "duration_hours": training.duration_hours,
                    "format": training.format,
                    "why": "Alignée avec vos compétences actuelles et le contexte de votre équipe.",
                }
            )

    return json.dumps(
        {
            "projects": current_project_names(emp),
            "recommendations": recommendations[:3],
        },
        ensure_ascii=False,
    )


async def get_manager_availability(db: AsyncSession, user_id: str, user_roles: list[str] | None = None, **kwargs) -> str:
    logger.info(f"Outil get_manager_availability() appelé pour user_id={user_id}")
    emp = await _get_employee(db, user_id)
    if not emp or not emp.manager_id:
        return json.dumps({"availability": [], "message": "Aucun manager identifié."}, ensure_ascii=False)

    slots = [
        {"date": slot.starts_at.strftime("%Y-%m-%d"), "time": slot.starts_at.strftime("%H:%M")}
        for slot in await calendar_connector.suggest_slots(db, emp.manager_id)
    ]
    return json.dumps({"availability": slots}, ensure_ascii=False)


async def schedule_one_on_one(
    db: AsyncSession,
    user_id: str,
    user_roles: list[str] | None = None,
    days_from_now: int = 5,
    **kwargs,
) -> str:
    logger.info(f"Outil schedule_one_on_one() appelé pour user_id={user_id}")
    emp = await _get_employee(db, user_id)
    if not emp or not emp.manager_id:
        return json.dumps({"error": "Manager introuvable pour ce collaborateur."}, ensure_ascii=False)

    interview = await calendar_connector.schedule_one_on_one(
        db,
        employee_id=emp.id,
        manager_id=emp.manager_id,
        title="1:1 de suivi",
        notes="Planifié par l'assistant IA à la demande du collaborateur.",
        preferred_days_from_now=max(1, days_from_now),
    )
    await db.commit()
    return json.dumps(
        {
            "scheduled": True,
            "date": interview.scheduled_at.strftime("%Y-%m-%d"),
            "time": interview.scheduled_at.strftime("%H:%M"),
            "message": "Le 1:1 a été ajouté au suivi manager côté plateforme.",
        },
        ensure_ascii=False,
    )



async def search_employee(db: AsyncSession, user_id: str, user_roles: list[str] | None = None, query: str = "", **kwargs) -> str:
    logger.info(f"Outil search_employee() appelé pour la requête '{query}'")
    db_query = select(Employee).filter(
        or_(
            Employee.first_name.ilike(f"%{query}%"),
            Employee.last_name.ilike(f"%{query}%")
        )
    ).limit(5)
    result = await db.execute(db_query)
    employees = result.scalars().all()
    
    if not employees:
        return json.dumps({"error": "Aucun employé trouvé avec ce nom."}, ensure_ascii=False)
        
    return json.dumps([{"id": e.id, "first_name": e.first_name, "last_name": e.last_name, "department_id": e.department_id} for e in employees], ensure_ascii=False)

async def get_employee_profile(db: AsyncSession, user_id: str, user_roles: list[str] | None = None, employee_id: str = "", **kwargs) -> str:
    logger.info(f"Outil get_employee_profile() appelé pour la cible '{employee_id}'")
    emp = await _get_employee(db, employee_id, options=[selectinload(Employee.department), selectinload(Employee.job)])
    if not emp:
        return json.dumps({"error": "Employé introuvable."}, ensure_ascii=False)
    
    current_emp = await _get_employee(db, user_id)
    scope = "self" if current_emp and emp.id == current_emp.id else "detail"
    
    from app.services.field_access_service import build_employee_access_context
    context = build_employee_access_context(current_emp, emp) if current_emp else {"is_self": False, "is_manager_of_target": False}

    payload = {
        "id": emp.id,
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "email": emp.email,
        "phone": emp.phone,
        "status": emp.status,
        "department": emp.department.name if emp.department else "Non assigné",
        "job_title": emp.job.title if emp.job else "Non défini",
    }
    
    return json.dumps(await _apply_tool_access(db, resource="employee", scope=scope, payload=payload, user_roles=user_roles, context=context), ensure_ascii=False)

async def get_employee_contracts(db: AsyncSession, user_id: str, user_roles: list[str] | None = None, employee_id: str = "", **kwargs) -> str:
    emp = await _get_employee(db, employee_id)
    if not emp:
        return json.dumps({"error": "Employé introuvable."}, ensure_ascii=False)
        
    current_emp = await _get_employee(db, user_id)
    scope = "self" if current_emp and emp.id == current_emp.id else "detail"
    
    from app.services.field_access_service import build_employee_access_context
    context = build_employee_access_context(current_emp, emp) if current_emp else {"is_self": False, "is_manager_of_target": False}

    # Si c'est un collaborateur qui demande pour quelqu'un d'autre, on bloque directement l'accès aux contrats
    primary_role = user_roles[0] if user_roles else "collaborator"
    if scope == "detail" and primary_role == "collaborator":
         return json.dumps({"error": "ACCES_REFUSE: Vous n'êtes pas autorisé à consulter les contrats d'autres employés."}, ensure_ascii=False)

    contracts_query = select(Contract).filter(Contract.employee_id == emp.id)
    contracts = (await db.execute(contracts_query)).scalars().all()
    
    contracts_payload = []
    for contract in contracts:
        contract_payload = await _apply_tool_access(
            db,
            resource="employee",
            scope=scope,
            payload={"contract_type": contract.contract_type, "salary": contract.salary},
            user_roles=user_roles,
            context=context
        )
        contracts_payload.append({
            "type": contract_payload.get("contract_type"),
            "start_date": contract.start_date.isoformat() if contract.start_date else None,
            "end_date": contract.end_date.isoformat() if contract.end_date else None,
            "salary": contract_payload.get("salary", "ACCES_REFUSE"),
            "is_active": contract.is_active,
            "_field_visibility": contract_payload.get("_field_visibility", {}),
        })
    return json.dumps({"contracts": contracts_payload}, ensure_ascii=False)

async def get_team_alerts(db: AsyncSession, user_id: str, user_roles: list[str] | None = None, **kwargs) -> str:
    if "manager" not in (user_roles or []) and "director" not in (user_roles or []):
        return json.dumps({"error": "Vous n'avez pas les droits pour voir les alertes d'équipe."}, ensure_ascii=False)
        
    query = select(Alert).filter(Alert.target_user_id == user_id, Alert.status == "open").order_by(Alert.created_at.desc()).limit(10)
    alerts = (await db.execute(query)).scalars().all()
    
    return json.dumps([{
        "title": a.title, "type": a.type, "severity": a.severity, "message": a.message, "created_at": a.created_at.isoformat() if a.created_at else None
    } for a in alerts], ensure_ascii=False)

# ════════════════════════════════════════════════════════════════
# Registre des outils (mapping nom → fonction)

# Registre des outils (mapping nom → fonction)
# ════════════════════════════════════════════════════════════════

TOOL_REGISTRY = {
    "get_employee_info": get_employee_info,
    "get_leave_balance": get_leave_balance,
    "get_contracts": get_contracts,
    "get_recent_attendances": get_recent_attendances,
    "generate_document": generate_document_tool,
    "get_my_tasks": get_my_tasks,
    "recommend_trainings": recommend_trainings,
    "get_manager_availability": get_manager_availability,

    "get_manager_availability": get_manager_availability,
    "schedule_one_on_one": schedule_one_on_one,
    "search_employee": search_employee,
    "get_employee_profile": get_employee_profile,
    "get_employee_contracts": get_employee_contracts,
    "get_team_alerts": get_team_alerts,
}



async def execute_tool(tool_name: str, arguments: dict, db: AsyncSession, user_id: str, user_roles: list[str] | None = None) -> str:
    """Exécuter un outil par son nom et retourner le résultat en JSON string."""
    if tool_name not in TOOL_REGISTRY:
        logger.error(f"Outil inconnu demandé par l'IA : {tool_name}")
        return json.dumps({"error": f"Outil '{tool_name}' non disponible"}, ensure_ascii=False)
    
    tool_fn = TOOL_REGISTRY[tool_name]
    logger.info(f"Exécution de l'outil : {tool_name}({arguments})")
    
    try:
        result = await tool_fn(db=db, user_id=user_id, user_roles=user_roles, **arguments)
        
        # Log de l'audit IA (Accès aux données)
        await ai_observability_service.log_event(
            db=db,
            user_id=user_id,
            event_type="ai_tool_call",
            status="success",
            details_json={"tool": tool_name, "arguments": arguments, "DAC_roles_used": user_roles}
        )
        
        logger.info(f"Outil {tool_name} exécuté avec succès")
        return result
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'outil {tool_name} : {e}")
        await ai_observability_service.log_event(
            db=db,
            user_id=user_id,
            event_type="ai_tool_call",
            status="error",
            details_json={"tool": tool_name, "error": str(e)}
        )
        return json.dumps({"error": f"Erreur lors de l'exécution de l'outil : {str(e)}"}, ensure_ascii=False)

import copy

async def get_dynamic_tool_definitions(db: AsyncSession) -> list[dict]:
    tools = copy.deepcopy(TOOL_DEFINITIONS)
    
    from app.models.domain import DocumentType
    result = await db.execute(select(DocumentType))
    doc_types = result.scalars().all()
    
    if not doc_types:
        return tools
        
    available_codes = [dt.code for dt in doc_types]
    names_list = ", ".join([f"{dt.name} (code: {dt.code})" for dt in doc_types])
    
    for tool in tools:
        if tool.get("function", {}).get("name") == "generate_document":
            desc = f"Générer un document RH officiel pour l'employé connecté. Types disponibles : {names_list}"
            tool["function"]["description"] = desc
            
            params = tool["function"].get("parameters", {}).get("properties", {}).get("document_type", {})
            params["enum"] = available_codes
            params["description"] = f"Le type de document à générer. Utilisez l'un des codes suivants : {', '.join(available_codes)}"
            break
            
    return tools

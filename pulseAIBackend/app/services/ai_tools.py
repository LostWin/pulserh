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
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.domain import Employee, Contract, Leave, Attendance, Task, Project, Department

logger = logging.getLogger("pulse.services.ai_tools")


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
]


# ════════════════════════════════════════════════════════════════
# Implémentation des fonctions d'outils
# ════════════════════════════════════════════════════════════════

async def get_employee_info(db: AsyncSession, user_id: str, **kwargs) -> str:
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
    
    return json.dumps({
        "id": emp.id,
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "email": emp.email,
        "phone": emp.phone,
        "hire_date": emp.hire_date.isoformat() if emp.hire_date else None,
        "status": emp.status,
        "department": emp.department.name if emp.department else "Non assigné",
        "job_title": emp.job.title if emp.job else "Non défini",
    }, ensure_ascii=False)


async def get_leave_balance(db: AsyncSession, user_id: str, **kwargs) -> str:
    """Consulter le solde de congés."""
    logger.info(f"Outil get_leave_balance() appelé pour user_id={user_id}")
    
    # Trouver l'employé
    emp_query = select(Employee).filter(
        (Employee.user_id == user_id) | (Employee.id == user_id)
    )
    emp_result = await db.execute(emp_query)
    emp = emp_result.scalar_one_or_none()
    
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
        (l.end_date - l.start_date).days + 1 
        for l in leaves 
        if l.status in ("Approuvé", "approved")
    )
    days_pending = sum(
        (l.end_date - l.start_date).days + 1 
        for l in leaves 
        if l.status in ("En attente", "pending")
    )
    
    return json.dumps({
        "total_annual_days": total_annual,
        "days_taken": days_taken,
        "days_pending": days_pending,
        "days_remaining": total_annual - days_taken,
        "recent_leaves": [
            {
                "type": l.leave_type,
                "start": l.start_date.isoformat(),
                "end": l.end_date.isoformat(),
                "status": l.status,
                "reason": l.reason,
            }
            for l in sorted(leaves, key=lambda x: x.start_date, reverse=True)[:5]
        ],
    }, ensure_ascii=False)


async def get_contracts(db: AsyncSession, user_id: str, **kwargs) -> str:
    """Récupérer les contrats actifs."""
    logger.info(f"Outil get_contracts() appelé pour user_id={user_id}")
    
    emp_query = select(Employee).filter(
        (Employee.user_id == user_id) | (Employee.id == user_id)
    )
    emp_result = await db.execute(emp_query)
    emp = emp_result.scalar_one_or_none()
    
    if not emp:
        return json.dumps({"error": "Employé non trouvé"}, ensure_ascii=False)
    
    contracts_query = select(Contract).filter(Contract.employee_id == emp.id)
    contracts_result = await db.execute(contracts_query)
    contracts = contracts_result.scalars().all()
    
    return json.dumps({
        "contracts": [
            {
                "type": c.contract_type,
                "start_date": c.start_date.isoformat() if c.start_date else None,
                "end_date": c.end_date.isoformat() if c.end_date else None,
                "salary": c.salary,
                "is_active": c.is_active,
            }
            for c in contracts
        ],
    }, ensure_ascii=False)


async def get_recent_attendances(db: AsyncSession, user_id: str, **kwargs) -> str:
    """Historique de présence récent (30 derniers jours)."""
    logger.info(f"Outil get_recent_attendances() appelé pour user_id={user_id}")
    
    emp_query = select(Employee).filter(
        (Employee.user_id == user_id) | (Employee.id == user_id)
    )
    emp_result = await db.execute(emp_query)
    emp = emp_result.scalar_one_or_none()
    
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


async def generate_document_tool(db: AsyncSession, user_id: str, document_type: str = "attestation_travail", **kwargs) -> str:
    """Générer un document RH via le DocumentGenerator."""
    logger.info(f"Outil generate_document() appelé | user_id={user_id}, type={document_type}")
    
    from app.services.document_generator import document_generator
    
    emp_query = select(Employee).options(
        selectinload(Employee.department),
        selectinload(Employee.job),
        selectinload(Employee.contracts)
    ).filter(
        (Employee.user_id == user_id) | (Employee.id == user_id)
    )
    emp_result = await db.execute(emp_query)
    emp = emp_result.scalar_one_or_none()
    
    if not emp:
        return json.dumps({"error": "Employé non trouvé, impossible de générer le document"}, ensure_ascii=False)
    
    salary = 0
    if emp.contracts and len(emp.contracts) > 0:
        salary = emp.contracts[0].salary
    
    context = {
        "employee": {
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "hire_date": emp.hire_date.strftime("%d/%m/%Y") if emp.hire_date else "N/A",
            "job_title": emp.job.title if emp.job else "Collaborateur",
            "department_name": emp.department.name if emp.department else "N/A",
        },
        "salary": f"{salary:,.2f}".replace(",", " "),
        "monthly_salary": f"{(salary / 12):,.2f}".replace(",", " "),
    }
    
    try:
        file_path = document_generator.create(doc_type=document_type, context=context)
        return json.dumps({
            "success": True,
            "document_type": document_type,
            "file_name": file_path.split("/")[-1],
            "message": f"Le document '{document_type}' a été généré avec succès. Il est disponible dans l'onglet Documents.",
        }, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erreur lors de la génération du document : {e}")
        return json.dumps({"error": f"Erreur lors de la génération : {str(e)}"}, ensure_ascii=False)


async def get_my_tasks(db: AsyncSession, user_id: str, **kwargs) -> str:
    """Récupérer les tâches et projets assignés."""
    logger.info(f"Outil get_my_tasks() appelé pour user_id={user_id}")
    
    emp_query = select(Employee).filter(
        (Employee.user_id == user_id) | (Employee.id == user_id)
    )
    emp_result = await db.execute(emp_query)
    emp = emp_result.scalar_one_or_none()
    
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


# ════════════════════════════════════════════════════════════════
# Registre des outils (mapping nom → fonction)
# ════════════════════════════════════════════════════════════════

TOOL_REGISTRY = {
    "get_employee_info": get_employee_info,
    "get_leave_balance": get_leave_balance,
    "get_contracts": get_contracts,
    "get_recent_attendances": get_recent_attendances,
    "generate_document": generate_document_tool,
    "get_my_tasks": get_my_tasks,
}


async def execute_tool(tool_name: str, arguments: dict, db: AsyncSession, user_id: str) -> str:
    """Exécuter un outil par son nom et retourner le résultat en JSON string."""
    if tool_name not in TOOL_REGISTRY:
        logger.error(f"Outil inconnu demandé par l'IA : {tool_name}")
        return json.dumps({"error": f"Outil '{tool_name}' non disponible"}, ensure_ascii=False)
    
    tool_fn = TOOL_REGISTRY[tool_name]
    logger.info(f"Exécution de l'outil : {tool_name}({arguments})")
    
    try:
        result = await tool_fn(db=db, user_id=user_id, **arguments)
        logger.info(f"Outil {tool_name} exécuté avec succès")
        return result
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'outil {tool_name} : {e}")
        return json.dumps({"error": f"Erreur lors de l'exécution de l'outil : {str(e)}"}, ensure_ascii=False)

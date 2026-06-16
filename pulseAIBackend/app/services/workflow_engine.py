"""
Moteur de workflows agentiques pour Pulse AI.

Orchestre les processus automatisés multi-étapes :
  - Onboarding (création compte AD, attribution matériel, envoi docs, etc.)
  - Offboarding (révocation accès, récupération matériel, solde de tout compte)

Chaque workflow est composé d'étapes séquentielles pilotées par un agent IA
qui peut appeler des APIs externes (Active Directory, GLPI, Horilla).

À implémenter par : Équipe Backend / Automatisation
"""

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any


logger = logging.getLogger("pulse.services.workflow_engine")


import asyncio
import uuid
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.database import AsyncSessionLocal
from app.models.domain import (
    Workflow, WorkflowStep, Employee, EmployeeSkill, Interview, Project, ProjectAssignment,
    TrainingCourse, TrainingEnrollment,
)
from app.services.alerting_service import alerting_service
from app.services.calendar_connector import calendar_connector
from app.services.employee_identity_service import sync_employee_identity
from app.services.hr_analytics_service import current_project_names
from app.services.offboarding_connector import offboarding_connector
from app.services.ai_observability_service import ai_observability_service

class WorkflowEngine:
    """
    Moteur d'exécution des workflows agentiques.
    """

    def __init__(self):
        logger.info("WorkflowEngine initialized")

    async def _load_employee_context(self, db: AsyncSession, employee_id: str) -> Employee | None:
        result_emp = await db.execute(
            select(Employee)
            .options(
                selectinload(Employee.job),
                selectinload(Employee.department),
                selectinload(Employee.manager).selectinload(Employee.job),
                selectinload(Employee.skills).selectinload(EmployeeSkill.skill),
                selectinload(Employee.training_enrollments).selectinload(TrainingEnrollment.training),
                selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
                selectinload(Employee.tasks),
                selectinload(Employee.contracts),
                selectinload(Employee.workflows).selectinload(Workflow.steps),
            )
            .filter(Employee.id == employee_id)
        )
        return result_emp.scalar_one_or_none()

    async def _recommended_trainings(self, db: AsyncSession, employee: Employee) -> list[TrainingCourse]:
        skill_ids = [item.skill_id for item in employee.skills]
        existing_training_ids = {item.training_id for item in employee.training_enrollments}
        query = select(TrainingCourse)
        trainings = (await db.execute(query)).scalars().all()
        recommendations = []
        for training in trainings:
            if training.id in existing_training_ids:
                continue
            if training.target_skill_id and training.target_skill_id in skill_ids:
                recommendations.append(training)
                continue
            if training.required_for_job_family and employee.job and training.required_for_job_family.lower() in employee.job.title.lower():
                recommendations.append(training)
        return recommendations[:3]

    async def _manager_availability_hint(self, db: AsyncSession, employee: Employee) -> str:
        if not employee.manager_id:
            return "Créer un point avec le manager dans la première semaine."
        slots = await calendar_connector.suggest_slots(db, employee.manager_id)
        if slots:
            return f"Proposer un 1:1 le {slots[0].label}."
        return "Prévoir un 1:1 manager dès qu'un créneau est libre cette quinzaine."

    def _default_onboarding_steps(
        self,
        employee: Employee,
        *,
        training_titles: list[str],
        project_names: list[str],
        manager_hint: str,
        context_docs: list[str],
    ) -> list[dict[str, Any]]:
        department = employee.department.name if employee.department else "Entreprise"
        job_title = employee.job.title if employee.job else "Collaborateur"
        first_project = project_names[0] if project_names else f"projets de l'équipe {department}"
        first_training = training_titles[0] if training_titles else "Parcours sécurité & RGPD"
        docs_hint = context_docs[0] if context_docs else "guide interne et documents RH validés"
        return [
            {
                "name": "Synchroniser les accès et le compte",
                "description": f"Créer ou vérifier les accès applicatifs du poste {job_title}, puis confirmer l'activation du compte utilisateur.",
                "step_type": "automated",
                "assigned_to": "equipe_it",
                "urgency": "high",
                "sequence": 1,
                "rationale": "L'accès aux outils est indispensable dès l'arrivée pour éviter un onboarding bloqué.",
            },
            {
                "name": "Partager les ressources de prise en main",
                "description": f"Mettre à disposition {docs_hint} et les documents de référence du département {department}.",
                "step_type": "manual",
                "assigned_to": "rh",
                "urgency": "medium",
                "sequence": 2,
                "rationale": "Le collaborateur doit disposer rapidement des repères documentaires validés.",
            },
            {
                "name": "Planifier le 1:1 manager",
                "description": f"Organiser un point d'intégration avec le manager. {manager_hint}",
                "step_type": "automated",
                "assigned_to": "manager",
                "urgency": "high",
                "sequence": 3,
                "rationale": "Le lien managérial précoce sécurise l'intégration et clarifie les attentes.",
            },
            {
                "name": "Affecter les formations prioritaires",
                "description": f"Inscrire le collaborateur à la formation '{first_training}' et compléter par les modules utiles au poste.",
                "step_type": "automated",
                "assigned_to": "rh",
                "urgency": "medium",
                "sequence": 4,
                "rationale": "Les compétences et obligations de conformité doivent être adressées dès les premières semaines.",
            },
            {
                "name": "Définir l'immersion projet",
                "description": f"Positionner le collaborateur sur {first_project} avec objectifs et interlocuteurs clés.",
                "step_type": "manual",
                "assigned_to": "manager",
                "urgency": "medium",
                "sequence": 5,
                "rationale": "L'ancrage concret dans l'équipe et les projets accélère l'autonomie.",
            },
        ]

    def _default_offboarding_steps(
        self,
        employee: Employee,
        *,
        departure_date: date,
        reason: str,
    ) -> list[dict[str, Any]]:
        project_names = current_project_names(employee)
        project_hint = project_names[0] if project_names else "ses dossiers actifs"
        departure_label = departure_date.strftime("%d/%m/%Y")
        return [
            {
                "name": "Préparer la checklist de sortie",
                "description": f"Valider avec RH les éléments de sortie pour un départ prévu le {departure_label}. Motif: {reason}.",
                "step_type": "manual",
                "assigned_to": "rh",
                "urgency": "high",
                "sequence": 1,
                "rationale": "Le cadrage administratif initial évite les oublis de conformité et d'information.",
            },
            {
                "name": "Révoquer les accès numériques",
                "description": "Désactiver le compte utilisateur et les accès internes à la date de sortie validée.",
                "step_type": "automated",
                "assigned_to": "equipe_it",
                "urgency": "high",
                "sequence": 2,
                "rationale": "La révocation des accès est une étape de sécurité prioritaire.",
            },
            {
                "name": "Planifier la restitution du matériel",
                "description": "Organiser la restitution du laptop, badge, tokens et autres équipements.",
                "step_type": "manual",
                "assigned_to": "equipe_it",
                "urgency": "medium",
                "sequence": 3,
                "rationale": "Le matériel et les supports d'accès doivent être récupérés et tracés.",
            },
            {
                "name": "Capturer le transfert de connaissances",
                "description": f"Documenter les points clés liés à {project_hint}, les contacts et les procédures à transmettre.",
                "step_type": "manual",
                "assigned_to": "manager",
                "urgency": "high",
                "sequence": 4,
                "rationale": "La continuité des activités dépend d'un transfert de connaissances structuré.",
            },
            {
                "name": "Clôturer l'administratif de sortie",
                "description": "Mettre à jour le statut RH, clôturer le contrat actif et archiver les éléments de sortie.",
                "step_type": "automated",
                "assigned_to": "rh",
                "urgency": "medium",
                "sequence": 5,
                "rationale": "La clôture administrative garantit la cohérence des référentiels internes.",
            },
        ]

    def _normalize_steps(self, steps: list[dict[str, Any]], fallback_steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
        normalized = []
        for index, step in enumerate(steps, start=1):
            normalized.append(
                {
                    "name": step.get("name") or f"Étape {index}",
                    "description": step.get("description", ""),
                    "step_type": step.get("step_type", "manual"),
                    "assigned_to": step.get("assigned_to", "rh"),
                    "urgency": step.get("urgency", "medium"),
                    "sequence": int(step.get("sequence", index)),
                    "rationale": step.get("rationale", ""),
                }
            )
        step_names = {item["name"].lower() for item in normalized}
        for fallback in fallback_steps:
            if fallback["name"].lower() not in step_names:
                normalized.append(fallback)
        return sorted(normalized, key=lambda item: item["sequence"])

    async def launch_workflow_execution(self, workflow_id: str) -> None:
        asyncio.create_task(self._execute_workflow(workflow_id))

    async def trigger_onboarding(self, employee_id: str) -> dict[str, Any]:
        """
        Déclencher un workflow d'onboarding complet (Phase de proposition).
        """
        workflow_id = str(uuid.uuid4())
        
        # 1. Créer le workflow en base avec le statut 'generating'
        async with AsyncSessionLocal() as db:
            try:
                workflow = Workflow(
                    id=workflow_id,
                    type="onboarding",
                    employee_id=employee_id,
                    status="generating",
                    progress_percent=0
                )
                db.add(workflow)
                await db.commit()
            except Exception as e:
                await db.rollback()
                logger.error(f"Error creating workflow: {e}")
                raise

        # 2. Lancer la génération IA en arrière-plan
        asyncio.create_task(self._generate_onboarding_proposal(workflow_id, employee_id))

        return {
            "id": workflow_id,
            "status": "generating",
            "message": "Génération de la proposition d'onboarding en cours..."
        }

    async def _generate_onboarding_proposal(self, workflow_id: str, employee_id: str):
        """
        Tâche de fond : appel LLM + RAG pour générer les étapes de l'onboarding.
        """
        start_time = time.time()
        logger.info(f"Starting async generation for workflow {workflow_id}")
        async with AsyncSessionLocal() as db:
            try:
                result_wf = await db.execute(select(Workflow).filter(Workflow.id == workflow_id))
                workflow = result_wf.scalar_one_or_none()
                if not workflow:
                    return

                employee = await self._load_employee_context(db, employee_id)
                
                if not employee:
                    workflow.status = "failed"
                    await db.commit()
                    await alerting_service.create_alert(
                        type="workflow_failed",
                        severity="critical",
                        payload={"reason": "employee_not_found"},
                        workflow_id=workflow_id,
                        title="Workflow en échec — collaborateur introuvable",
                        message="Le workflow n'a pas pu être généré car le collaborateur est introuvable.",
                        target_roles=["hr", "director"],
                        link="/rh/workflows",
                    )
                    return

                job_title = employee.job.title if employee.job else "Nouvel Employé"
                department = employee.department.name if employee.department else "Entreprise"
                training_recommendations = await self._recommended_trainings(db, employee)
                training_titles = [training.title for training in training_recommendations]
                project_names = current_project_names(employee)
                manager_hint = await self._manager_availability_hint(db, employee)

                from app.services.rag_service import rag_service
                rag_results = await rag_service.search_documents(
                    query=f"Onboarding manuels formations pour le poste {job_title} dans le département {department}",
                    user_role=["rh"],
                    top_k=3
                )
                
                context_docs = ""
                context_doc_labels: list[str] = []
                if rag_results:
                    context_doc_labels = [doc["source_file"] for doc in rag_results]
                    context_docs = "DOCUMENTS INTERNES TROUVÉS :\n" + "\n".join(
                        [f"- Source: {doc['source_file']}\nContenu: {doc['snippet']}" for doc in rag_results]
                    )
                
                # Appel LLM pour générer le JSON
                from app.services.llm_client import llm_client
                system_prompt = f"""Tu es un expert RH de PulseAI. Ton rôle est de concevoir un parcours d'onboarding sur 30 jours parfaitement adapté au rôle '{job_title}' dans le département '{department}'.
Tu dois générer le résultat sous forme de JSON structuré contenant une liste d'étapes. Ne renvoie RIEN D'AUTRE que le JSON valide.
Applique une stricte minimisation de données: n'introduis jamais d'information personnelle ou confidentielle qui n'est pas nécessaire à l'exécution des étapes.
Tu dois absolument prendre en compte:
- les formations recommandées: {', '.join(training_titles) if training_titles else 'aucune formation spécifique identifiée'}
- les projets ou contextes d'équipe: {', '.join(project_names) if project_names else 'pas encore de projet assigné'}
- la disponibilité managériale indicative: {manager_hint}

Format JSON attendu :
{{
    "steps": [
        {{
            "name": "Titre court de l'étape",
            "description": "Description détaillée de l'action à réaliser.",
            "step_type": "automated" | "manual" | "external_ticket",
            "assigned_to": "equipe_it" | "manager" | "{employee_id}",
            "urgency": "low" | "medium" | "high",
            "sequence": 1,
            "rationale": "Justification de l'importance de cette étape et de son placement temporel."
        }}
    ]
}}

{context_docs}
"""
                
                try:
                    llm_response = await llm_client.generate(
                        prompt="Génère le plan complet d'onboarding. Utilise le contexte documentaire si pertinent. Rédige au moins 5 étapes essentielles incluant accès, documents, 1:1 manager, formations et immersion projet.",
                        system_prompt=system_prompt,
                        temperature=0.4,
                        max_tokens=2500
                    )
                    
                    import json
                    # Nettoyer d'éventuels backticks markdown
                    json_str = llm_response.strip()
                    if json_str.startswith("```json"):
                        json_str = json_str[7:]
                    if json_str.startswith("```"):
                        json_str = json_str[3:]
                    if json_str.endswith("```"):
                        json_str = json_str[:-3]
                        
                    parsed_data = json.loads(json_str.strip())
                    steps_data = parsed_data.get("steps", [])
                    
                    await ai_observability_service.log_event(
                        db=db,
                        user_id=None,
                        event_type="workflow",
                        status="success",
                        duration_ms=int((time.time() - start_time) * 1000),
                        details_json={"workflow_id": workflow_id, "action": "generate_onboarding"}
                    )
                    
                except Exception as e:
                    logger.warning(f"Erreur de génération LLM ou parsing JSON : {e}. Fallback déterministe utilisé.")
                    await ai_observability_service.log_event(
                        db=db,
                        user_id=None,
                        event_type="workflow",
                        status="error",
                        duration_ms=int((time.time() - start_time) * 1000),
                        details_json={"workflow_id": workflow_id, "error": str(e), "action": "generate_onboarding_fallback"}
                    )
                    steps_data = []

                fallback_steps = self._default_onboarding_steps(
                    employee,
                    training_titles=training_titles,
                    project_names=project_names,
                    manager_hint=manager_hint,
                    context_docs=context_doc_labels,
                )

                normalized_steps = self._normalize_steps(steps_data, fallback_steps)

                for idx, data in enumerate(normalized_steps):
                    step = WorkflowStep(
                        workflow_id=workflow_id,
                        name=data.get("name", "Étape sans nom"),
                        description=data.get("description", ""),
                        step_type=data.get("step_type", "manual"),
                        assigned_to=data.get("assigned_to", "rh"),
                        urgency=data.get("urgency", "medium"),
                        sequence=data.get("sequence", idx + 1),
                        rationale=data.get("rationale", ""),
                        status="pending"
                    )
                    db.add(step)
                
                # Mettre à jour le statut du workflow à 'draft'
                workflow.status = "draft"
                await db.commit()
                
                await alerting_service.create_alert(
                    type="workflow_review",
                    severity="medium",
                    payload={"workflow_status": "draft"},
                    employee_id=employee_id,
                    workflow_id=workflow_id,
                    title=f"Workflow à valider — {employee.first_name} {employee.last_name}",
                    message=f"Le workflow {workflow.type} généré par l'IA attend une validation RH.",
                    target_roles=["hr"],
                    link="/rh/workflows",
                )
                logger.info(f"Workflow {workflow_id} generated and ready for review (status: draft)")

            except Exception as e:
                logger.error(f"Error in background generation: {e}")
                if 'workflow' in locals() and workflow:
                    workflow.status = "failed"
                    await db.commit()
                await alerting_service.create_alert(
                    type="workflow_failed",
                    severity="critical",
                    payload={"reason": "background_generation_error", "error": str(e)},
                    employee_id=employee_id,
                    workflow_id=workflow_id,
                    title="Workflow en échec",
                    message="Une erreur serveur a interrompu la génération du workflow.",
                    target_roles=["hr", "director"],
                    link="/rh/workflows",
                )

    async def trigger_offboarding(
        self, employee_id: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        context = context or {}
        workflow_id = str(uuid.uuid4())
        departure_date = context.get("departure_date") or date.today()
        if isinstance(departure_date, str):
            departure_date = date.fromisoformat(departure_date)
        reason = context.get("reason") or "Départ collaborateur"

        async with AsyncSessionLocal() as db:
            employee = await self._load_employee_context(db, employee_id)
            if not employee:
                raise ValueError("Collaborateur introuvable pour l'offboarding.")

            workflow = Workflow(
                id=workflow_id,
                type="offboarding",
                employee_id=employee_id,
                status="draft",
                progress_percent=0,
            )
            db.add(workflow)
            await db.flush()

            steps = self._default_offboarding_steps(employee, departure_date=departure_date, reason=reason)
            for index, data in enumerate(steps, start=1):
                db.add(
                    WorkflowStep(
                        workflow_id=workflow_id,
                        name=data["name"],
                        description=data["description"],
                        step_type=data["step_type"],
                        assigned_to=data["assigned_to"],
                        urgency=data["urgency"],
                        sequence=index,
                        rationale=data["rationale"],
                        due_date=datetime.combine(departure_date, datetime.min.time(), tzinfo=timezone.utc),
                        status="pending",
                    )
                )
            await db.commit()

            await alerting_service.create_alert(
                type="workflow_review",
                severity="medium",
                payload={"workflow_status": "draft", "reason": reason},
                employee_id=employee_id,
                workflow_id=workflow_id,
                title=f"Offboarding à valider — {employee.first_name} {employee.last_name}",
                message="Le workflow d'offboarding est prêt pour validation RH.",
                target_roles=["hr"],
                link="/rh/workflows",
            )

        return {
            "id": workflow_id,
            "status": "draft",
            "message": "Proposition d'offboarding prête pour validation RH.",
        }

    async def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Workflow)
                .options(
                    selectinload(Workflow.steps),
                    selectinload(Workflow.employee).selectinload(Employee.department),
                    selectinload(Workflow.employee).selectinload(Employee.job),
                )
                .filter(Workflow.id == workflow_id)
            )
            workflow = result.scalar_one_or_none()
            if not workflow:
                return {}
            
            steps = []
            for s in workflow.steps:
                steps.append({
                    "id": s.id,
                    "name": s.name,
                    "status": s.status,
                    "rationale": s.rationale,
                    "step_type": s.step_type,
                    "assigned_to": s.assigned_to
                })

            return {
                "id": workflow.id,
                "type": workflow.type,
                "employee_id": workflow.employee_id,
                "employee_name": f"{workflow.employee.first_name} {workflow.employee.last_name}" if workflow.employee else None,
                "job_title": workflow.employee.job.title if workflow.employee and workflow.employee.job else None,
                "department": workflow.employee.department.name if workflow.employee and workflow.employee.department else None,
                "status": workflow.status,
                "progress_percent": workflow.progress_percent,
                "created_at": workflow.created_at,
                "steps": steps
            }

    async def retry_step(self, workflow_id: str, step_id: str) -> dict[str, Any]:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Workflow).options(selectinload(Workflow.steps)).filter(Workflow.id == workflow_id)
            )
            workflow = result.scalar_one_or_none()
            if not workflow:
                raise ValueError("Workflow introuvable.")
            step = next((item for item in workflow.steps if item.id == step_id), None)
            if not step:
                raise ValueError("Étape introuvable.")
            step.status = "pending"
            step.executed_at = None
            workflow.status = "running"
            await db.commit()
        await self.launch_workflow_execution(workflow_id)
        return {"status": "retrying", "workflow_id": workflow_id, "step_id": step_id}

    async def _execute_workflow(self, workflow_id: str) -> None:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Workflow)
                .options(selectinload(Workflow.steps))
                .filter(Workflow.id == workflow_id)
            )
            workflow = result.scalar_one_or_none()
            if not workflow:
                return
            employee = await self._load_employee_context(db, workflow.employee_id)
            if not employee:
                workflow.status = "failed"
                await db.commit()
                return

            ordered_steps = sorted(workflow.steps, key=lambda item: item.sequence)
            total_steps = max(1, len(ordered_steps))

            for index, step in enumerate(ordered_steps, start=1):
                if step.status == "done":
                    continue
                step.status = "running"
                await db.commit()
                try:
                    await self._execute_step(db, workflow, step, employee)
                    step.status = "done"
                    step.executed_at = datetime.now(timezone.utc)
                    workflow.progress_percent = round((index / total_steps) * 100)
                    await db.commit()
                except Exception as exc:
                    logger.error("Workflow step failed %s/%s: %s", workflow_id, step.id, exc)
                    step.status = "failed"
                    workflow.status = "failed"
                    await db.commit()
                    await alerting_service.create_alert(
                        type="workflow_failed",
                        severity="high",
                        payload={"reason": "step_failed", "step": step.name, "error": str(exc)},
                        employee_id=employee.id,
                        workflow_id=workflow.id,
                        title=f"Échec étape workflow — {step.name}",
                        message=f"L'étape '{step.name}' a échoué et nécessite une reprise RH.",
                        target_roles=["hr", "director"],
                        link="/rh/workflows",
                    )
                    return

            workflow.status = "completed"
            workflow.progress_percent = 100
            await db.commit()
            await alerting_service.create_alert(
                type="workflow_completed",
                severity="low",
                payload={"workflow_type": workflow.type},
                employee_id=employee.id,
                workflow_id=workflow.id,
                title=f"Workflow {workflow.type} terminé",
                message=f"Le workflow {workflow.type} de {employee.first_name} {employee.last_name} est terminé.",
                target_roles=["hr"],
                link="/rh/workflows",
            )

    async def _execute_step(self, db: AsyncSession, workflow: Workflow, step: WorkflowStep, employee: Employee) -> None:
        action_name = step.name.lower()
        if workflow.type == "onboarding":
            if "accès" in action_name or "compte" in action_name:
                await sync_employee_identity(employee.id, db)
                return
            if "formations" in action_name:
                recommendations = await self._recommended_trainings(db, employee)
                existing = {enrollment.training_id for enrollment in employee.training_enrollments}
                for training in recommendations:
                    if training.id in existing:
                        continue
                    db.add(
                        TrainingEnrollment(
                            employee_id=employee.id,
                            training_id=training.id,
                            status="assigned",
                            assigned_at=datetime.now(timezone.utc),
                            due_date=date.today() + timedelta(days=21),
                            mandatory=False,
                        )
                    )
                await db.flush()
                return
            if "1:1" in action_name or "manager" in action_name:
                if employee.manager_id:
                    existing = (
                        await db.execute(
                            select(Interview).where(
                                Interview.employee_id == employee.id,
                                Interview.manager_id == employee.manager_id,
                                Interview.title.ilike("%intégration%"),
                            )
                        )
                    ).scalar_one_or_none()
                    if not existing:
                        await calendar_connector.schedule_one_on_one(
                            db,
                            employee_id=employee.id,
                            manager_id=employee.manager_id,
                            title="Entretien d'intégration",
                            notes="Point d'intégration déclenché par le workflow onboarding.",
                            preferred_days_from_now=5,
                        )
                return
            if "immersion projet" in action_name:
                if not employee.project_assignments:
                    project = (
                        await db.execute(select(Project).where(Project.name == "Onboarding Demo"))
                    ).scalar_one_or_none()
                    if not project:
                        project = Project(name="Onboarding Demo", description="Projet support onboarding", status="En cours")
                        db.add(project)
                        await db.flush()
                    db.add(
                        ProjectAssignment(
                            project_id=project.id,
                            employee_id=employee.id,
                            role_on_project="Contributeur",
                            allocation_pct=50,
                            start_date=date.today(),
                            is_active=True,
                        )
                    )
                    await db.flush()
                return

        if workflow.type == "offboarding":
            if "révoquer les accès" in action_name:
                await offboarding_connector.revoke_access(db, employee)
                return
            if "restitution du matériel" in action_name:
                await offboarding_connector.register_asset_recovery(db, employee, step)
                await db.flush()
                return
            if "clôturer l'administratif" in action_name:
                await offboarding_connector.close_hr_record(db, employee)
                await db.flush()
                return
            if "transfert de connaissances" in action_name:
                await offboarding_connector.create_knowledge_transfer(db, employee, step)
                await db.flush()
                return

        if step.step_type == "external_ticket" and not step.external_ticket_id:
            step.external_ticket_id = f"TCK-{workflow.id[:8].upper()}-{step.sequence}"
            await db.flush()

# Singleton
workflow_engine = WorkflowEngine()

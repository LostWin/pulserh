import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.workflow import (
    OnboardingRequest, OffboardingRequest, 
    WorkflowResponse, StepResponse, WorkflowApproveRequest
)
from app.core.rbac import require_hr
from app.services.workflow_engine import workflow_engine
from app.database import AsyncSessionLocal
from app.models.domain import Workflow, WorkflowStep
from sqlalchemy.future import select

router = APIRouter(prefix="/workflows", tags=["Workflows"])
logger = logging.getLogger(__name__)

@router.post("/onboarding", dependencies=[Depends(require_hr)])
async def trigger_onboarding(request: OnboardingRequest):
    """Déclencher un onboarding agentique (Phase de génération)"""
    logger.info(f"Triggered onboarding generation for employee {request.employee_id}")
    return await workflow_engine.trigger_onboarding(request.employee_id)

@router.post("/{id}/approve", response_model=WorkflowResponse, dependencies=[Depends(require_hr)])
async def approve_workflow(id: str, request: WorkflowApproveRequest):
    """Approuver et lancer un workflow 'draft' (avec éventuelles modifications)"""
    logger.info(f"Approving workflow {id}")
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Workflow).filter(Workflow.id == id))
        workflow = result.scalar_one_or_none()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        if workflow.status != "draft":
            raise HTTPException(status_code=400, detail="Workflow is not in draft state")
        
        # Mettre à jour les étapes avec celles modifiées par le RH
        # Pour simplifier on met à jour les descriptions/assigned_to
        for new_step in request.steps:
            res_step = await db.execute(select(WorkflowStep).filter(WorkflowStep.id == new_step.id, WorkflowStep.workflow_id == id))
            db_step = res_step.scalar_one_or_none()
            if db_step:
                db_step.name = new_step.name
                db_step.description = new_step.description
                db_step.assigned_to = new_step.assigned_to
                db_step.urgency = new_step.urgency
                db_step.sequence = new_step.sequence
                db_step.step_type = new_step.step_type
        
        workflow.status = "running"
        await db.commit()
        await workflow_engine.launch_workflow_execution(id)
        return await workflow_engine.get_workflow_status(id)


@router.post("/offboarding", dependencies=[Depends(require_hr)])
async def trigger_offboarding(request: OffboardingRequest):
    """Déclencher un offboarding agentique"""
    return await workflow_engine.trigger_offboarding(
        request.employee_id,
        context={
            "departure_date": request.departure_date.isoformat(),
            "reason": request.reason,
        },
    )

@router.get("/", response_model=List[WorkflowResponse], dependencies=[Depends(require_hr)])
async def list_workflows():
    """Liste des workflows actifs"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Workflow))
        workflows = result.scalars().all()
        result_wfs = []
        for w in workflows:
            result_wfs.append(await workflow_engine.get_workflow_status(w.id))
        return result_wfs

@router.get("/{id}", response_model=WorkflowResponse, dependencies=[Depends(require_hr)])
async def get_workflow(id: str):
    """Détail et avancement d'un workflow"""
    status = await workflow_engine.get_workflow_status(id)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return status

@router.post("/{id}/steps/{step_id}/retry", dependencies=[Depends(require_hr)])
async def retry_workflow_step(id: str, step_id: str):
    """Forcer l'exécution d'une étape (utile si l'agent a échoué)"""
    return await workflow_engine.retry_step(id, step_id)

@router.get("/{id}/steps", response_model=List[StepResponse], dependencies=[Depends(require_hr)])
async def list_workflow_steps(id: str):
    """Liste des étapes avec statuts"""
    status = await workflow_engine.get_workflow_status(id)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return status.get("steps", [])

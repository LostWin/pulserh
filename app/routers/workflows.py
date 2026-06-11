import logging
import uuid
from typing import List
from fastapi import APIRouter, Depends

from app.schemas.workflow import (
    OnboardingRequest, OffboardingRequest, 
    WorkflowResponse, StepResponse
)
from app.core.rbac import require_hr

router = APIRouter(prefix="/workflows", tags=["Workflows"])
logger = logging.getLogger(__name__)

@router.post("/onboarding", response_model=WorkflowResponse, dependencies=[Depends(require_hr)])
def trigger_onboarding(request: OnboardingRequest):
    """Déclencher un onboarding agentique"""
    workflow_id = str(uuid.uuid4())
    logger.info(f"Triggered onboarding workflow {workflow_id} for employee {request.employee_id}")
    return WorkflowResponse(
        id=workflow_id,
        type="onboarding",
        employee_id=request.employee_id,
        status="running",
        progress_percent=0,
        steps=[]
    )

@router.post("/offboarding", response_model=WorkflowResponse, dependencies=[Depends(require_hr)])
def trigger_offboarding(request: OffboardingRequest):
    """Déclencher un offboarding agentique"""
    workflow_id = str(uuid.uuid4())
    logger.info(f"Triggered offboarding workflow {workflow_id} for employee {request.employee_id}")
    return WorkflowResponse(
        id=workflow_id,
        type="offboarding",
        employee_id=request.employee_id,
        status="running",
        progress_percent=0,
        steps=[]
    )

@router.get("/", response_model=List[WorkflowResponse], dependencies=[Depends(require_hr)])
def list_workflows():
    """Liste des workflows actifs"""
    return []

@router.get("/{id}", response_model=WorkflowResponse, dependencies=[Depends(require_hr)])
def get_workflow(id: str):
    """Détail et avancement d'un workflow"""
    return WorkflowResponse(
        id=id,
        type="onboarding",
        employee_id="emp-123",
        status="running",
        progress_percent=50,
        steps=[]
    )

@router.post("/{id}/steps/{step_id}/retry", dependencies=[Depends(require_hr)])
def retry_workflow_step(id: str, step_id: str):
    """Forcer l'exécution d'une étape (utile si l'agent a échoué)"""
    logger.info(f"Retrying step {step_id} for workflow {id}")
    return {"status": "Retry triggered", "workflow_id": id, "step_id": step_id}

@router.get("/{id}/steps", response_model=List[StepResponse], dependencies=[Depends(require_hr)])
def list_workflow_steps(id: str):
    """Liste des étapes avec statuts"""
    return [
        StepResponse(id="step-1", name="Création compte AD", status="done"),
        StepResponse(id="step-2", name="Attribution matériel", status="failed")
    ]
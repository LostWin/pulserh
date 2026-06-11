import logging
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.prediction import (
    RiskScoreResponse, TurnoverProjectionResponse, MonthProjection,
    SimulationRequest, SimulationResponse
)
from app.schemas.auth import CurrentUser
from app.dependencies import get_current_user
from app.core.rbac import require_any_role

router = APIRouter(prefix="/predict", tags=["Predictions"])
logger = logging.getLogger(__name__)

# Dépendances RBAC
risk_roles = require_any_role("manager", "hr", "director")
team_risk_roles = require_any_role("manager", "hr")
turnover_roles = require_any_role("hr", "director")
simulate_roles = require_any_role("director", "hr")

@router.get("/risk/{employee_id}", response_model=RiskScoreResponse, dependencies=[Depends(risk_roles)])
def get_employee_risk(employee_id: str, current_user: CurrentUser = Depends(get_current_user)):
    """Score de désengagement d'un employé"""
    
    # Règle métier : Un manager ne consulte le risque que de son équipe
    if "hr" not in current_user.roles and "director" not in current_user.roles:
        # Stub: Vérifier que l'employé appartient à l'équipe du manager
        is_in_team = True # Remplacer par check DB
        if not is_in_team:
            raise HTTPException(status_code=403, detail="Cet employé n'est pas dans votre équipe.")
            
    # Stub: Appel au modèle prédictif (ex: XGBoost)
    return RiskScoreResponse(
        employee_id=employee_id,
        score=0.85, # 85% de risque de départ
        level="red",
        computed_at=datetime.now(timezone.utc)
    )

@router.get("/risk", response_model=List[RiskScoreResponse], dependencies=[Depends(team_risk_roles)])
def get_team_risks(current_user: CurrentUser = Depends(get_current_user)):
    """Scores pour toute l'équipe/tous les employés"""
    # Stub: Si hr -> tous les employés. Si manager -> seulement son équipe.
    return []

@router.get("/turnover", response_model=TurnoverProjectionResponse, dependencies=[Depends(turnover_roles)])
def get_turnover_projection():
    """Projection turnover à 6 mois"""
    # Stub: Données projetées
    return TurnoverProjectionResponse(
        months=[
            MonthProjection(month="2026-07", projected_departures=5, confidence=0.9),
            MonthProjection(month="2026-08", projected_departures=3, confidence=0.85)
        ]
    )

@router.post("/simulate", response_model=SimulationResponse, dependencies=[Depends(simulate_roles)])
def simulate_scenario(request: SimulationRequest):
    """Simulation scénario (ex: +5% salaire)"""
    logger.info(f"Simulation demandée : {request.scenario_type} avec params {request.parameters}")
    
    # Stub: Appel au simulateur ML
    return SimulationResponse(
        impact_description=f"L'application du scénario '{request.scenario_type}' réduirait l'insatisfaction salariale globale.",
        projected_turnover_change=-1.5 # Baisse de 1.5% du turnover
    )
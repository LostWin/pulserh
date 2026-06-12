import logging
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, Response

from app.schemas.dashboard import KPIsResponse, HeadcountResponse
from app.schemas.auth import CurrentUser
from app.dependencies import get_current_user
from app.core.rbac import require_hr, require_any_role

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
logger = logging.getLogger(__name__)

# Dépendances RBAC communes
kpi_roles = require_any_role("hr", "manager", "director")
hr_director_roles = require_any_role("hr", "director")

# Classe utilitaire pour injecter facilement les filtres communs
class DashboardFilters:
    def __init__(
        self,
        period_start: Optional[date] = Query(None, description="Date de début"),
        period_end: Optional[date] = Query(None, description="Date de fin"),
        department_id: Optional[str] = Query(None, description="Filtre sur un département"),
        entity_id: Optional[str] = Query(None, description="Filtre sur une entité légale")
    ):
        self.period_start = period_start
        self.period_end = period_end
        self.department_id = department_id
        self.entity_id = entity_id

@router.get("/kpis", response_model=KPIsResponse, dependencies=[Depends(kpi_roles)])
def get_kpis(filters: DashboardFilters = Depends(), current_user: CurrentUser = Depends(get_current_user)):
    """KPIs consolidés (effectifs, turnover, absentéisme)"""
    # Si le user est manager, la requête SQL (côté service) 
    # devra filtrer automatiquement les KPIs pour ne concerner que son équipe
    return KPIsResponse(
        headcount=150,
        turnover_rate=5.2,
        absenteeism_rate=2.1,
        avg_salary=45000.0
    )

@router.get("/headcount", response_model=HeadcountResponse, dependencies=[Depends(hr_director_roles)])
def get_headcount(filters: DashboardFilters = Depends()):
    """Effectifs par département/contrat/site"""
    return HeadcountResponse(
        by_department=[{"department": "IT", "count": 50}],
        by_contract_type=[{"contract": "CDI", "count": 120}, {"contract": "CDD", "count": 30}],
        by_site=[{"site": "Paris", "count": 100}, {"site": "Lyon", "count": 50}]
    )

@router.get("/absenteeism", dependencies=[Depends(kpi_roles)])
def get_absenteeism(filters: DashboardFilters = Depends(), current_user: CurrentUser = Depends(get_current_user)):
    """Taux d'absentéisme"""
    return {"status": "ok", "absenteeism_rate": 2.1, "details": []}

@router.get("/salary-mass", dependencies=[Depends(hr_director_roles)])
def get_salary_mass(filters: DashboardFilters = Depends()):
    """Masse salariale et projections"""
    return {"status": "ok", "total_mass": 5000000, "projected_mass": 5200000}

@router.get("/age-pyramid", dependencies=[Depends(hr_director_roles)])
def get_age_pyramid(filters: DashboardFilters = Depends()):
    """Données pour pyramide des âges"""
    return {"status": "ok", "bins": []}

@router.get("/export", dependencies=[Depends(hr_director_roles)])
def export_dashboard(filters: DashboardFilters = Depends()):
    """Export CSV/Excel du dashboard"""
    # Stub: Retourner un fichier CSV fictif
    return Response(content="metric,value\nheadcount,150", media_type="text/csv")

@router.post("/reports/generate", dependencies=[Depends(require_hr)])
def generate_monthly_report(filters: DashboardFilters = Depends()):
    """Générer un rapport PDF mensuel"""
    logger.info("Generating monthly PDF report for dashboard")
    # Retour asynchrone (stub)
    return {"status": "Report generation started", "job_id": "job-456"}
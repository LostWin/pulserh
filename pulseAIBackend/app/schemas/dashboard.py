from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class KPIsResponse(BaseModel):
    headcount: int
    turnover_rate: float
    absenteeism_rate: float
    avg_salary: float
    # On peut ajouter d'autres métriques si nécessaire

class HeadcountResponse(BaseModel):
    by_department: List[Dict[str, Any]] # ex: [{"department": "IT", "count": 10}]
    by_contract_type: List[Dict[str, Any]]
    by_site: List[Dict[str, Any]]


class RHDepartmentDashboardItem(BaseModel):
    id: str
    name: str
    headcount: int
    engagement: int
    risk: int
    metrics_source: Dict[str, str]


class RHSummaryStats(BaseModel):
    headcount: int
    global_engagement: int
    turnover_predicted: float
    active_risks: int


class RHDashboardResponse(BaseModel):
    summary: RHSummaryStats
    departments: List[RHDepartmentDashboardItem]
    generated_at: str


class DashboardDocumentItem(BaseModel):
    id: str
    name: str
    type: str
    date: str
    size: str


class CollaboratorOnboardingItem(BaseModel):
    label: str
    done: bool
    date_label: Optional[str] = None


class CollaboratorDashboardSummary(BaseModel):
    first_name: str
    leave_current_balance: int
    leave_total_balance: int
    benefits_status: str
    next_benefits_enrollment: str
    primary_benefit_label: Optional[str] = None
    performance_score: float
    performance_target_label: str
    career_focus_title: Optional[str] = None
    mobility_status: Optional[str] = None
    documents_total: int
    documents_pending: int
    policies_total: int
    compliance_score: int


class CollaboratorDashboardResponse(BaseModel):
    summary: CollaboratorDashboardSummary
    onboarding: List[CollaboratorOnboardingItem]
    recent_documents: List[DashboardDocumentItem]
    generated_at: str


class ManagerTeamMember(BaseModel):
    id: str
    name: str
    title: str
    department: str
    engagement: int
    risk: str
    delta: int
    tenure: str
    last_active: str
    signal: str
    risk_score: int
    factors: List[Dict[str, Any]]
    recommendation: str
    performance_score: Optional[float] = None
    focus_objective_title: Optional[str] = None
    focus_objective_progress_pct: Optional[int] = None
    benefits_status: Optional[str] = None
    mobility_status: Optional[str] = None


class ManagerTrendPoint(BaseModel):
    month: str
    engagement: int
    risque: int


class ManagerAlertItem(BaseModel):
    id: str
    level: str
    text: str
    time: str
    route: Optional[str] = None


class ManagerDashboardSummaryStats(BaseModel):
    team_size: int
    avg_engagement: int
    at_risk_count: int
    interviews_to_schedule: int
    mobility_requests_open: int = 0


class ManagerDashboardResponse(BaseModel):
    summary: ManagerDashboardSummaryStats
    trend: List[ManagerTrendPoint]
    team: List[ManagerTeamMember]
    alerts: List[ManagerAlertItem]
    generated_at: str


class DirectionAlertItem(BaseModel):
    level: str
    text: str
    impact: str


class DirectionDepartmentItem(BaseModel):
    id: str
    name: str
    headcount: int
    engagement: int


class DirectionTurnoverSavedItem(BaseModel):
    month: str
    economie: float
    depart: int


class DirectionSummaryStats(BaseModel):
    global_engagement: int
    turnover_saved_total: float
    roi_ia: float
    headcount: int


class DirectionDashboardResponse(BaseModel):
    summary: DirectionSummaryStats
    turnover_saved: List[DirectionTurnoverSavedItem]
    departments: List[DirectionDepartmentItem]
    alerts: List[DirectionAlertItem]
    generated_at: str

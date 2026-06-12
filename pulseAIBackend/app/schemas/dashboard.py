from pydantic import BaseModel
from typing import List, Dict, Any

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
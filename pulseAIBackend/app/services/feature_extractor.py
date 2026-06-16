from datetime import date, timedelta

import pandas as pd
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Attendance, Contract, Employee, Leave, Task

# Encodage numérique du type de contrat
CONTRACT_ENCODING = {"CDI": 0, "CDD": 1, "Alternance": 2, "Stage": 3}


class FeatureExtractor:
    """Construit le vecteur de features utilisé par le modèle XGBoost."""

    async def get_employee_features(self, employee_id: str, db: AsyncSession) -> dict:
        today = date.today()

        emp = (await db.execute(
            select(Employee).where(Employee.id == employee_id)
        )).scalar_one_or_none()

        if not emp:
            raise ValueError(f"Employé {employee_id} introuvable")

        tenure_months = (today - emp.hire_date).days // 30

        # Contrat actif pour le salaire et le type de contrat
        contract = (await db.execute(
            select(Contract).where(
                and_(Contract.employee_id == employee_id, Contract.is_active == True)
            )
        )).scalar_one_or_none()

        salary = contract.salary if contract else 0.0
        contract_type = CONTRACT_ENCODING.get(contract.contract_type, -1) if contract else -1

        # Congés approuvés sur les 12 derniers mois
        leaves = (await db.execute(
            select(Leave).where(
                and_(
                    Leave.employee_id == employee_id,
                    Leave.status == "Approuvé",
                    Leave.start_date >= today - timedelta(days=365),
                )
            )
        )).scalars().all()

        leave_days_12m = sum((l.end_date - l.start_date).days + 1 for l in leaves)
        sick_leave_count_12m = sum(1 for l in leaves if l.leave_type == "Maladie")

        # Présences sur les 3 derniers mois
        statuses = (await db.execute(
            select(Attendance.status).where(
                and_(
                    Attendance.employee_id == employee_id,
                    Attendance.date >= today - timedelta(days=90),
                )
            )
        )).scalars().all()

        absence_count_3m = statuses.count("Absent")
        late_count_3m = statuses.count("Retard")

        # Performance sur les tâches assignées
        tasks = (await db.execute(
            select(Task).where(Task.assignee_id == employee_id)
        )).scalars().all()

        scored = [t.evaluation_score for t in tasks if t.status == "Terminé" and t.evaluation_score is not None]
        avg_task_score = sum(scored) / len(scored) if scored else 0.0

        overdue_tasks_count = sum(
            1 for t in tasks if t.due_date and t.due_date < today and t.status != "Terminé"
        )

        return {
            "employee_id": employee_id,
            "tenure_months": tenure_months,
            "salary": salary,
            "contract_type": contract_type,
            "leave_days_12m": leave_days_12m,
            "sick_leave_count_12m": sick_leave_count_12m,
            "absence_count_3m": absence_count_3m,
            "late_count_3m": late_count_3m,
            "avg_task_score": avg_task_score,
            "overdue_tasks_count": overdue_tasks_count,
        }

    async def get_training_data(self, db: AsyncSession) -> pd.DataFrame:
        """Retourne la matrice de features pour tous les employés.
        Le label (churned) est dérivé du statut 'inactif'.
        """
        employees = (await db.execute(
            select(Employee.id, Employee.status)
        )).all()

        rows = []
        for emp_id, emp_status in employees:
            try:
                features = await self.get_employee_features(emp_id, db)
                features["churned"] = 1 if emp_status == "inactif" else 0
                rows.append(features)
            except ValueError:
                continue

        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.drop(columns=["employee_id"])
        return df


feature_extractor = FeatureExtractor()

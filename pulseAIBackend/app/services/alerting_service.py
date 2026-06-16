import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from sqlalchemy import Text, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models.domain import (
    Alert,
    AlertRecipientState,
    Employee,
    Workflow,
)
from app.schemas.auth import CurrentUser
from app.services.websocket_manager import websocket_manager

logger = logging.getLogger("pulse.services.alerting")


class AlertingService:
    def __init__(self):
        logger.info("AlertingService initialized")

    async def create_alert(
        self,
        type: str,
        severity: Literal["low", "medium", "critical"],
        payload: dict[str, Any],
        employee_id: str | None = None,
        workflow_id: str | None = None,
        title: str | None = None,
        message: str | None = None,
        target_roles: list[str] | None = None,
        target_user_id: str | None = None,
        source: str = "pulse_ai",
        link: str | None = None,
        fingerprint: str | None = None,
        db: AsyncSession | None = None,
    ) -> dict[str, Any]:
        should_close = False
        if db is None:
            db = AsyncSessionLocal()
            should_close = True

        try:
            alert_fingerprint = fingerprint or self._build_fingerprint(type, employee_id, workflow_id, payload)
            query = select(Alert).filter(Alert.fingerprint == alert_fingerprint)
            result = await db.execute(query)
            alert = result.scalar_one_or_none()

            if alert:
                alert.severity = severity
                alert.title = title or alert.title
                alert.message = message or alert.message
                alert.status = "open"
                alert.payload = payload
                alert.target_roles = target_roles or alert.target_roles
                alert.target_user_id = target_user_id or alert.target_user_id
                alert.link = link or alert.link
                alert.source = source
                alert.employee_id = employee_id or alert.employee_id
                alert.workflow_id = workflow_id or alert.workflow_id
            else:
                alert = Alert(
                    fingerprint=alert_fingerprint,
                    type=type,
                    severity=severity,
                    title=title or self._default_title(type, employee_id),
                    message=message or self._default_message(type, payload),
                    status="open",
                    source=source,
                    employee_id=employee_id,
                    workflow_id=workflow_id,
                    target_roles=target_roles,
                    target_user_id=target_user_id,
                    link=link,
                    payload=payload,
                )
                db.add(alert)

            await db.commit()
            await db.refresh(alert)
            await websocket_manager.broadcast_alert(
                event_type="alert.upsert",
                alert=self._serialize_alert(alert, None),
                target_user_id=alert.target_user_id,
                target_roles=alert.target_roles,
            )
            return {"id": alert.id, "status": alert.status}
        except Exception:
            await db.rollback()
            raise
        finally:
            if should_close:
                await db.close()

    async def mark_as_read(self, alert_id: str, user_id: str, db: AsyncSession | None = None) -> dict[str, Any]:
        return await self._update_recipient_state(alert_id, user_id, mark_read=True, db=db)

    async def archive_alert(self, alert_id: str, user_id: str, db: AsyncSession | None = None) -> dict[str, Any]:
        return await self._update_recipient_state(alert_id, user_id, mark_archive=True, db=db)

    async def resolve_alert(self, alert_id: str, resolved_by: str, db: AsyncSession | None = None) -> dict[str, Any]:
        should_close = False
        if db is None:
            db = AsyncSessionLocal()
            should_close = True

        try:
            result = await db.execute(select(Alert).filter(Alert.id == alert_id))
            alert = result.scalar_one_or_none()
            if not alert:
                raise ValueError("Alert not found")

            alert.status = "resolved"
            alert.resolved_by = resolved_by
            alert.resolved_at = datetime.now(timezone.utc)
            await db.commit()
            await websocket_manager.broadcast_alert(
                event_type="alert.upsert",
                alert=self._serialize_alert(alert, None),
                target_user_id=alert.target_user_id,
                target_roles=alert.target_roles,
            )
            return {"status": "resolved", "id": alert_id}
        except Exception:
            await db.rollback()
            raise
        finally:
            if should_close:
                await db.close()

    async def set_action_plan(self, alert_id: str, description: str, db: AsyncSession | None = None) -> dict[str, Any]:
        should_close = False
        if db is None:
            db = AsyncSessionLocal()
            should_close = True

        try:
            result = await db.execute(select(Alert).filter(Alert.id == alert_id))
            alert = result.scalar_one_or_none()
            if not alert:
                raise ValueError("Alert not found")

            alert.action_plan = description
            alert.status = "in_progress"
            await db.commit()
            await websocket_manager.broadcast_alert(
                event_type="alert.upsert",
                alert=self._serialize_alert(alert, None),
                target_user_id=alert.target_user_id,
                target_roles=alert.target_roles,
            )
            return {"status": "action_plan_set", "id": alert_id}
        except Exception:
            await db.rollback()
            raise
        finally:
            if should_close:
                await db.close()

    async def list_alerts_for_user(
        self,
        current_user: CurrentUser,
        filters: dict[str, Any] | None = None,
        db: AsyncSession | None = None,
    ) -> list[dict[str, Any]]:
        should_close = False
        if db is None:
            db = AsyncSessionLocal()
            should_close = True

        try:
            await self.sync_alerts(db)

            role_filters = [Alert.target_roles.cast(Text).ilike(f'%"{role}"%') for role in current_user.roles]
            query = (
                select(Alert)
                .options(selectinload(Alert.employee).selectinload(Employee.department))
                .filter(
                    or_(
                        Alert.target_user_id == current_user.id,
                        *role_filters,
                    )
                )
                .order_by(Alert.created_at.desc())
            )

            if filters:
                if filters.get("severity"):
                    query = query.filter(Alert.severity == filters["severity"])
                if filters.get("status"):
                    query = query.filter(Alert.status == filters["status"])
                if filters.get("employee_id"):
                    query = query.filter(Alert.employee_id == filters["employee_id"])
                if filters.get("type"):
                    query = query.filter(Alert.type == filters["type"])

            result = await db.execute(query)
            alerts = result.scalars().all()

            alert_ids = [alert.id for alert in alerts]
            state_result = await db.execute(
                select(AlertRecipientState).filter(
                    AlertRecipientState.user_id == current_user.id,
                    AlertRecipientState.alert_id.in_(alert_ids),
                )
            ) if alert_ids else None
            states = {state.alert_id: state for state in state_result.scalars().all()} if state_result else {}

            visible_alerts = []
            for alert in alerts:
                if "manager" in current_user.roles and alert.target_user_id and alert.target_user_id != current_user.id:
                    continue
                state = states.get(alert.id)
                if state and state.archived_at:
                    continue
                visible_alerts.append(self._serialize_alert(alert, state))

            return visible_alerts
        finally:
            if should_close:
                await db.close()

    async def get_alert_for_user(self, alert_id: str, current_user: CurrentUser, db: AsyncSession | None = None) -> dict[str, Any] | None:
        alerts = await self.list_alerts_for_user(current_user, db=db)
        for alert in alerts:
            if alert["id"] == alert_id:
                return alert
        return None

    async def sync_alerts(self, db: AsyncSession) -> dict[str, int]:
        created = 0
        updated = 0

        created += await self._sync_absence_alerts(db)
        created += await self._sync_overdue_task_alerts(db)
        workflow_stats = await self._sync_workflow_alerts(db)
        created += workflow_stats["created"]
        updated += workflow_stats["updated"]

        return {"created": created, "updated": updated}

    async def _sync_absence_alerts(self, db: AsyncSession) -> int:
        since = datetime.now(timezone.utc).date() - timedelta(days=30)
        attendance_query = (
            select(Employee)
            .options(selectinload(Employee.manager), selectinload(Employee.department), selectinload(Employee.attendances))
        )
        result = await db.execute(attendance_query)
        employees = result.scalars().all()

        created = 0
        for employee in employees:
            absent_count = sum(
                1 for attendance in employee.attendances
                if attendance.status.lower() == "absent" and attendance.date and attendance.date >= since
            )
            fingerprint = f"absence:{employee.id}"
            if absent_count >= 3:
                manager_user_id = employee.manager.user_id if employee.manager else None
                payload = {"absent_count": absent_count, "window_days": 30}
                employee_name = f"{employee.first_name} {employee.last_name}"
                if manager_user_id:
                    await self.create_alert(
                        type="attendance_absence",
                        severity="medium",
                        payload=payload,
                        employee_id=employee.id,
                        title=f"Absences répétées — {employee_name}",
                        message=f"{employee_name} a {absent_count} absences sur les 30 derniers jours.",
                        target_user_id=manager_user_id,
                        target_roles=["manager"],
                        link=f"/manager/equipe/{employee.id}",
                        fingerprint=f"{fingerprint}:manager",
                        db=db,
                    )
                    created += 1

                await self.create_alert(
                    type="attendance_absence",
                    severity="critical",
                    payload=payload,
                    employee_id=employee.id,
                    title=f"Absence à surveiller — {employee_name}",
                    message=f"{employee_name} a cumulé {absent_count} absences sur 30 jours.",
                    target_roles=["hr"],
                    link=f"/rh/employes/{employee.id}",
                    fingerprint=f"{fingerprint}:hr",
                    db=db,
                )
                created += 1
            else:
                await self._resolve_by_fingerprints(db, [f"{fingerprint}:manager", f"{fingerprint}:hr"])
        return created

    async def _sync_overdue_task_alerts(self, db: AsyncSession) -> int:
        today = datetime.now(timezone.utc).date()
        task_query = select(Employee).options(selectinload(Employee.tasks), selectinload(Employee.manager))
        result = await db.execute(task_query)
        employees = result.scalars().all()

        created = 0
        for employee in employees:
            overdue_tasks = [
                task for task in employee.tasks
                if task.due_date and task.due_date < today and task.status != "Terminé"
            ]
            fingerprint = f"tasks_overdue:{employee.id}"
            if len(overdue_tasks) >= 2 and employee.manager and employee.manager.user_id:
                employee_name = f"{employee.first_name} {employee.last_name}"
                await self.create_alert(
                    type="tasks_overdue",
                    severity="medium",
                    payload={"count": len(overdue_tasks)},
                    employee_id=employee.id,
                    title=f"Tâches en retard — {employee_name}",
                    message=f"{len(overdue_tasks)} tâches sont en retard pour {employee_name}.",
                    target_user_id=employee.manager.user_id,
                    target_roles=["manager"],
                    link=f"/manager/equipe/{employee.id}",
                    fingerprint=f"{fingerprint}:manager",
                    db=db,
                )
                created += 1
            else:
                await self._resolve_by_fingerprints(db, [f"{fingerprint}:manager"])
        return created

    async def _sync_workflow_alerts(self, db: AsyncSession) -> dict[str, int]:
        query = (
            select(Workflow)
            .options(
                selectinload(Workflow.employee).selectinload(Employee.department),
                selectinload(Workflow.steps),
            )
        )
        result = await db.execute(query)
        workflows = result.scalars().all()
        created = 0
        updated = 0
        now = datetime.now(timezone.utc)

        for workflow in workflows:
            employee_name = "Collaborateur"
            if workflow.employee:
                employee_name = f"{workflow.employee.first_name} {workflow.employee.last_name}"

            if workflow.status == "draft":
                await self.create_alert(
                    type="workflow_review",
                    severity="medium",
                    payload={"workflow_status": workflow.status},
                    employee_id=workflow.employee_id,
                    workflow_id=workflow.id,
                    title=f"Workflow à valider — {employee_name}",
                    message=f"Le workflow {workflow.type} attend une validation RH.",
                    target_roles=["hr"],
                    link="/rh/workflows",
                    fingerprint=f"workflow_review:{workflow.id}",
                    db=db,
                )
                created += 1
            else:
                await self._resolve_by_fingerprints(db, [f"workflow_review:{workflow.id}"])

            if workflow.status == "failed":
                await self.create_alert(
                    type="workflow_failed",
                    severity="critical",
                    payload={"workflow_status": workflow.status},
                    employee_id=workflow.employee_id,
                    workflow_id=workflow.id,
                    title=f"Workflow en échec — {employee_name}",
                    message=f"Le workflow {workflow.type} est en échec et requiert une reprise RH.",
                    target_roles=["hr", "director"],
                    link="/rh/workflows",
                    fingerprint=f"workflow_failed:{workflow.id}",
                    db=db,
                )
                created += 1
            else:
                await self._resolve_by_fingerprints(db, [f"workflow_failed:{workflow.id}"])

            overdue_step_fingerprints = []
            for step in workflow.steps:
                fingerprint = f"workflow_step_delayed:{step.id}"
                overdue_step_fingerprints.append(fingerprint)
                if step.due_date and step.due_date < now and step.status in {"pending", "running"}:
                    await self.create_alert(
                        type="workflow_step_delayed",
                        severity="critical",
                        payload={"step_name": step.name, "assigned_to": step.assigned_to},
                        employee_id=workflow.employee_id,
                        workflow_id=workflow.id,
                        title=f"Étape bloquée — {step.name}",
                        message=f"L'étape '{step.name}' du workflow {workflow.type} est en retard.",
                        target_roles=["hr"],
                        link="/rh/workflows",
                        fingerprint=fingerprint,
                        db=db,
                    )
                    updated += 1
                else:
                    await self._resolve_by_fingerprints(db, [fingerprint])

        return {"created": created, "updated": updated}

    async def _resolve_by_fingerprints(self, db: AsyncSession, fingerprints: list[str]) -> None:
        if not fingerprints:
            return
        result = await db.execute(select(Alert).filter(Alert.fingerprint.in_(fingerprints), Alert.status != "resolved"))
        alerts = result.scalars().all()
        for alert in alerts:
            alert.status = "resolved"
            alert.resolved_at = datetime.now(timezone.utc)
        if alerts:
            await db.commit()

    async def _update_recipient_state(
        self,
        alert_id: str,
        user_id: str,
        mark_read: bool = False,
        mark_archive: bool = False,
        db: AsyncSession | None = None,
    ) -> dict[str, Any]:
        should_close = False
        if db is None:
            db = AsyncSessionLocal()
            should_close = True

        try:
            result = await db.execute(
                select(AlertRecipientState).filter(
                    AlertRecipientState.alert_id == alert_id,
                    AlertRecipientState.user_id == user_id,
                )
            )
            state = result.scalar_one_or_none()
            if not state:
                state = AlertRecipientState(alert_id=alert_id, user_id=user_id)
                db.add(state)

            now = datetime.now(timezone.utc)
            if mark_read:
                state.read_at = now
            if mark_archive:
                state.read_at = state.read_at or now
                state.archived_at = now

            await db.commit()
            await websocket_manager.broadcast_user_event(
                event_type="alert.state",
                user_id=user_id,
                data={
                    "alertId": alert_id,
                    "read": bool(state.read_at),
                    "archived": bool(state.archived_at),
                },
            )
            return {"status": "ok", "id": alert_id}
        except Exception:
            await db.rollback()
            raise
        finally:
            if should_close:
                await db.close()

    def _serialize_alert(self, alert: Alert, state: AlertRecipientState | None) -> dict[str, Any]:
        employee_name = None
        department = None
        if alert.employee:
            employee_name = f"{alert.employee.first_name} {alert.employee.last_name}"
            if alert.employee.department:
                department = alert.employee.department.name

        return {
            "id": alert.id,
            "type": alert.type,
            "severity": alert.severity,
            "title": alert.title,
            "employee_id": alert.employee_id,
            "employee_name": employee_name,
            "workflow_id": alert.workflow_id,
            "department": department,
            "message": alert.message or "",
            "link": alert.link,
            "source": alert.source,
            "created_at": alert.created_at,
            "status": alert.status,
            "is_read": bool(state and state.read_at),
            "is_archived": bool(state and state.archived_at),
            "action_plan": alert.action_plan,
            "payload": alert.payload,
        }

    def _build_fingerprint(self, type: str, employee_id: str | None, workflow_id: str | None, payload: dict[str, Any]) -> str:
        payload_marker = payload.get("step_name") or payload.get("count") or payload.get("workflow_status") or "generic"
        return f"{type}:{employee_id or 'none'}:{workflow_id or 'none'}:{payload_marker}"

    def _default_title(self, alert_type: str, employee_id: str | None) -> str:
        if employee_id:
            return f"Alerte {alert_type} sur {employee_id}"
        return f"Alerte {alert_type}"

    def _default_message(self, alert_type: str, payload: dict[str, Any]) -> str:
        if payload:
            return f"{alert_type} détectée avec contexte: {payload}"
        return f"Alerte {alert_type} détectée."


alerting_service = AlertingService()

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol

import httpx
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.domain import Employee, Interview


@dataclass
class CalendarSlot:
    starts_at: datetime
    label: str


@dataclass
class CalendarIntegrationStatus:
    provider: str
    configured: bool
    active_provider: str
    fallback_in_use: bool
    details: str


class CalendarProvider(Protocol):
    async def suggest_slots(self, db: AsyncSession, manager: Employee, *, days_ahead: int | None = None) -> list[CalendarSlot]: ...
    async def schedule_one_on_one(
        self,
        db: AsyncSession,
        *,
        employee: Employee,
        manager: Employee,
        title: str,
        notes: str,
        preferred_days_from_now: int = 5,
    ) -> Interview: ...
    def is_configured(self) -> bool: ...
    def provider_name(self) -> str: ...


class InternalCalendarProvider:
    def provider_name(self) -> str:
        return "internal"

    def is_configured(self) -> bool:
        return True

    async def suggest_slots(self, db: AsyncSession, manager: Employee, *, days_ahead: int | None = None) -> list[CalendarSlot]:
        lookahead = days_ahead or settings.CALENDAR_LOOKAHEAD_DAYS
        interviews = (
            await db.execute(
                select(Interview)
                .where(Interview.manager_id == manager.id)
                .order_by(Interview.scheduled_at.asc())
            )
        ).scalars().all()
        now = datetime.now(timezone.utc)
        slots: list[CalendarSlot] = []
        for offset in range(2, lookahead + 1):
            candidate = now + timedelta(days=offset)
            if candidate.weekday() >= 5:
                continue
            slot = candidate.replace(
                hour=settings.CALENDAR_DEFAULT_MEETING_HOUR,
                minute=0,
                second=0,
                microsecond=0,
            )
            has_conflict = any(
                interview.scheduled_at.date() == slot.date()
                and abs((interview.scheduled_at - slot).total_seconds()) < 90 * 60
                for interview in interviews
                if interview.scheduled_at >= now
            )
            if has_conflict:
                continue
            slots.append(CalendarSlot(starts_at=slot, label=slot.strftime("%d/%m à %Hh%M")))
            if len(slots) == 3:
                break
        return slots

    async def schedule_one_on_one(
        self,
        db: AsyncSession,
        *,
        employee: Employee,
        manager: Employee,
        title: str,
        notes: str,
        preferred_days_from_now: int = 5,
    ) -> Interview:
        slots = await self.suggest_slots(db, manager, days_ahead=max(preferred_days_from_now, 3) + 7)
        chosen = slots[0].starts_at if slots else datetime.now(timezone.utc) + timedelta(days=max(preferred_days_from_now, 3))
        interview = Interview(
            employee_id=employee.id,
            manager_id=manager.id,
            title=title,
            scheduled_at=chosen,
            status="Planifié",
            location="Visio / bureau manager",
            notes=notes,
        )
        db.add(interview)
        await db.flush()
        return interview


class MicrosoftGraphCalendarProvider:
    def provider_name(self) -> str:
        return "microsoft"

    def is_configured(self) -> bool:
        return all([settings.MICROSOFT_TENANT_ID, settings.MICROSOFT_CLIENT_ID, settings.MICROSOFT_CLIENT_SECRET])

    async def _get_access_token(self) -> str:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/token",
                data={
                    "client_id": settings.MICROSOFT_CLIENT_ID,
                    "client_secret": settings.MICROSOFT_CLIENT_SECRET,
                    "scope": "https://graph.microsoft.com/.default",
                    "grant_type": "client_credentials",
                },
            )
            response.raise_for_status()
            return response.json()["access_token"]

    async def suggest_slots(self, db: AsyncSession, manager: Employee, *, days_ahead: int | None = None) -> list[CalendarSlot]:
        if not manager.email:
            return []
        lookahead = days_ahead or settings.CALENDAR_LOOKAHEAD_DAYS
        token = await self._get_access_token()
        start = datetime.now(timezone.utc) + timedelta(days=2)
        end = start + timedelta(days=lookahead)
        payload = {
            "schedules": [manager.email],
            "startTime": {"dateTime": start.isoformat(), "timeZone": "UTC"},
            "endTime": {"dateTime": end.isoformat(), "timeZone": "UTC"},
            "availabilityViewInterval": 60,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{settings.MICROSOFT_GRAPH_BASE_URL}/users/{manager.email}/calendar/getSchedule",
                headers={"Authorization": f"Bearer {token}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        busy = set()
        for item in data.get("value", []):
            for slot in item.get("scheduleItems", []):
                busy.add(slot["start"]["dateTime"][:10])

        slots = []
        cursor = start
        while cursor <= end and len(slots) < 3:
            if cursor.weekday() < 5 and cursor.date().isoformat() not in busy:
                slot = cursor.replace(hour=settings.CALENDAR_DEFAULT_MEETING_HOUR, minute=0, second=0, microsecond=0)
                slots.append(CalendarSlot(starts_at=slot, label=slot.strftime("%d/%m à %Hh%M")))
            cursor += timedelta(days=1)
        return slots

    async def schedule_one_on_one(
        self,
        db: AsyncSession,
        *,
        employee: Employee,
        manager: Employee,
        title: str,
        notes: str,
        preferred_days_from_now: int = 5,
    ) -> Interview:
        slots = await self.suggest_slots(db, manager, days_ahead=max(preferred_days_from_now, 3) + 7)
        chosen = slots[0].starts_at if slots else datetime.now(timezone.utc) + timedelta(days=max(preferred_days_from_now, 3))
        token = await self._get_access_token()
        payload = {
            "subject": title,
            "body": {"contentType": "Text", "content": notes},
            "start": {"dateTime": chosen.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": (chosen + timedelta(minutes=45)).isoformat(), "timeZone": "UTC"},
            "attendees": [{"emailAddress": {"address": employee.email, "name": f"{employee.first_name} {employee.last_name}"}, "type": "required"}],
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{settings.MICROSOFT_GRAPH_BASE_URL}/users/{manager.email}/events",
                headers={"Authorization": f"Bearer {token}"},
                json=payload,
            )
            response.raise_for_status()
            remote_event = response.json()

        interview = Interview(
            employee_id=employee.id,
            manager_id=manager.id,
            title=title,
            scheduled_at=chosen,
            status="Planifié",
            location="Calendrier Microsoft 365",
            notes=f"{notes}\nEvent: {remote_event.get('webLink', '')}".strip(),
        )
        db.add(interview)
        await db.flush()
        return interview


class GoogleCalendarProvider:
    def provider_name(self) -> str:
        return "google"

    def is_configured(self) -> bool:
        return all([settings.GOOGLE_CLIENT_EMAIL, settings.GOOGLE_PRIVATE_KEY])

    async def _get_access_token(self, subject: str | None = None) -> str:
        issued_at = int(datetime.now(timezone.utc).timestamp())
        scopes = settings.GOOGLE_CALENDAR_SCOPES.strip()
        assertion_payload = {
            "iss": settings.GOOGLE_CLIENT_EMAIL,
            "scope": scopes,
            "aud": "https://oauth2.googleapis.com/token",
            "exp": issued_at + 3600,
            "iat": issued_at,
        }
        delegated_user = subject or settings.GOOGLE_CALENDAR_IMPERSONATION_USER
        if delegated_user:
            assertion_payload["sub"] = delegated_user

        private_key = settings.GOOGLE_PRIVATE_KEY.replace("\\n", "\n")
        signed_jwt = jwt.encode(assertion_payload, private_key, algorithm="RS256")

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "assertion": signed_jwt,
                },
            )
            response.raise_for_status()
            return response.json()["access_token"]

    async def suggest_slots(self, db: AsyncSession, manager: Employee, *, days_ahead: int | None = None) -> list[CalendarSlot]:
        if not manager.email:
            return []
        lookahead = days_ahead or settings.CALENDAR_LOOKAHEAD_DAYS
        token = await self._get_access_token(subject=manager.email)
        start = datetime.now(timezone.utc) + timedelta(days=2)
        end = start + timedelta(days=lookahead)
        payload = {
            "timeMin": start.isoformat(),
            "timeMax": end.isoformat(),
            "items": [{"id": manager.email}],
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://www.googleapis.com/calendar/v3/freeBusy",
                headers={"Authorization": f"Bearer {token}"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        busy = {
            item["start"][:10]
            for item in data.get("calendars", {}).get(manager.email, {}).get("busy", [])
        }
        slots = []
        cursor = start
        while cursor <= end and len(slots) < 3:
            if cursor.weekday() < 5 and cursor.date().isoformat() not in busy:
                slot = cursor.replace(hour=settings.CALENDAR_DEFAULT_MEETING_HOUR, minute=0, second=0, microsecond=0)
                slots.append(CalendarSlot(starts_at=slot, label=slot.strftime("%d/%m à %Hh%M")))
            cursor += timedelta(days=1)
        return slots

    async def schedule_one_on_one(
        self,
        db: AsyncSession,
        *,
        employee: Employee,
        manager: Employee,
        title: str,
        notes: str,
        preferred_days_from_now: int = 5,
    ) -> Interview:
        slots = await self.suggest_slots(db, manager, days_ahead=max(preferred_days_from_now, 3) + 7)
        chosen = slots[0].starts_at if slots else datetime.now(timezone.utc) + timedelta(days=max(preferred_days_from_now, 3))
        token = await self._get_access_token(subject=manager.email)
        payload = {
            "summary": title,
            "description": notes,
            "start": {"dateTime": chosen.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": (chosen + timedelta(minutes=45)).isoformat(), "timeZone": "UTC"},
            "attendees": [{"email": employee.email}],
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"https://www.googleapis.com/calendar/v3/calendars/{manager.email}/events",
                headers={"Authorization": f"Bearer {token}"},
                json=payload,
            )
            response.raise_for_status()
            remote_event = response.json()

        interview = Interview(
            employee_id=employee.id,
            manager_id=manager.id,
            title=title,
            scheduled_at=chosen,
            status="Planifié",
            location="Google Calendar",
            notes=f"{notes}\nEvent: {remote_event.get('htmlLink', '')}".strip(),
        )
        db.add(interview)
        await db.flush()
        return interview


class CalendarConnector:
    def __init__(self) -> None:
        self.internal_provider = InternalCalendarProvider()
        self.providers: dict[str, CalendarProvider] = {
            "internal": self.internal_provider,
            "microsoft": MicrosoftGraphCalendarProvider(),
            "google": GoogleCalendarProvider(),
        }

    def _configured_provider(self) -> CalendarProvider:
        provider = self.providers.get(settings.CALENDAR_PROVIDER, self.internal_provider)
        if provider.is_configured():
            return provider
        return self.internal_provider

    async def _load_manager(self, db: AsyncSession, manager_id: str) -> Employee | None:
        return (
            await db.execute(select(Employee).where(Employee.id == manager_id))
        ).scalar_one_or_none()

    def get_status(self) -> CalendarIntegrationStatus:
        requested = self.providers.get(settings.CALENDAR_PROVIDER, self.internal_provider)
        active = self._configured_provider()
        configured = requested.is_configured()
        if requested.provider_name() == "internal":
            details = "Le provider interne utilise les entretiens planifiés dans Pulse AI."
        elif configured:
            details = f"Le provider {requested.provider_name()} est configuré et peut être utilisé."
        else:
            details = f"Le provider {requested.provider_name()} est demandé mais incomplet; fallback interne actif."
        return CalendarIntegrationStatus(
            provider=requested.provider_name(),
            configured=configured,
            active_provider=active.provider_name(),
            fallback_in_use=active.provider_name() != requested.provider_name(),
            details=details,
        )

    async def suggest_slots(self, db: AsyncSession, manager_id: str, *, days_ahead: int | None = None) -> list[CalendarSlot]:
        manager = await self._load_manager(db, manager_id)
        if not manager:
            return []
        provider = self._configured_provider()
        return await provider.suggest_slots(db, manager, days_ahead=days_ahead)

    async def schedule_one_on_one(
        self,
        db: AsyncSession,
        *,
        employee_id: str,
        manager_id: str,
        title: str,
        notes: str,
        preferred_days_from_now: int = 5,
    ) -> Interview:
        employee = (await db.execute(select(Employee).where(Employee.id == employee_id))).scalar_one_or_none()
        manager = await self._load_manager(db, manager_id)
        if not employee or not manager:
            raise ValueError("Impossible de charger le collaborateur ou le manager pour le calendrier.")
        provider = self._configured_provider()
        return await provider.schedule_one_on_one(
            db,
            employee=employee,
            manager=manager,
            title=title,
            notes=notes,
            preferred_days_from_now=preferred_days_from_now,
        )


calendar_connector = CalendarConnector()

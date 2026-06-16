from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.rbac import require_any_role
from app.database import get_db
from app.dependencies import get_current_user
from app.models.domain import Department, Employee, GeneratedReport
from app.schemas.auth import CurrentUser
from app.schemas.report import ReportCreate, ReportItem, ReportListResponse
from app.services.secure_document_storage import secure_document_storage
from app.services.export_service import render_pdf, render_csv, render_xlsx

router = APIRouter(prefix="/reports", tags=["Reports"])
direction_roles = require_any_role("director", "hr")


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} o"
    if size_bytes < 1024 * 1024:
        return f"{round(size_bytes / 1024)} Ko"
    return f"{round(size_bytes / (1024 * 1024), 1)} Mo"


def _build_report_payload(name: str, period: str, dept: str, employees: list[Employee]) -> list[dict[str, str]]:
    return [
        {
            "Employé": f"{employee.first_name} {employee.last_name}",
            "Email": employee.email,
            "Département": employee.department.name if employee.department else "Non assigné",
            "Poste": employee.job.title if employee.job else "Non assigné",
            "Statut": employee.status,
            "Période": period,
            "Filtre": dept,
        }
        for employee in employees
    ]





@router.get("", response_model=ReportListResponse, dependencies=[Depends(direction_roles)])
async def list_reports(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GeneratedReport).order_by(GeneratedReport.created_at.desc()))
    items = result.scalars().all()
    departments = await db.execute(select(Department.name).order_by(Department.name.asc()))
    return ReportListResponse(
        items=[
            ReportItem(
                id=item.id,
                name=item.name,
                period=item.period,
                dept=item.department_filter or "Tous",
                generated=item.created_at.strftime("%d %b %Y") if item.created_at else "",
                size=item.size or "—",
                format=item.format,
                status=item.status,
            )
            for item in items
        ],
        available_departments=["Tous", *[row[0] for row in departments.all()]],
    )


@router.post("/generate", response_model=ReportItem, dependencies=[Depends(direction_roles)])
async def generate_report(
    payload: ReportCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Employee).options(selectinload(Employee.department), selectinload(Employee.job))
    if payload.dept and payload.dept != "Tous":
        query = query.join(Department, Department.id == Employee.department_id).filter(Department.name == payload.dept)
    result = await db.execute(query.limit(150))
    employees = result.scalars().all()
    rows = _build_report_payload(payload.name, payload.period, payload.dept, employees)

    fmt = payload.format.upper()
    if fmt == "PDF":
        file_bytes = render_pdf(payload.name, payload.period, payload.dept, rows)
    elif fmt == "XLSX":
        file_bytes = render_xlsx(rows)
    else:
        file_bytes = render_csv(rows)
        if fmt != "CSV":
            fmt = "CSV"

    storage_uri = secure_document_storage.upload_bytes(file_bytes, f"{payload.name.replace(' ', '_')}.{fmt.lower()}", "generated")
    report = GeneratedReport(
        name=payload.name,
        period=payload.period,
        department_filter=payload.dept,
        format=fmt,
        file_path=storage_uri,
        size=_format_size(len(file_bytes)),
        status="ready",
        created_by=current_user.email,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return ReportItem(
        id=report.id,
        name=report.name,
        period=report.period,
        dept=report.department_filter or "Tous",
        generated=report.created_at.strftime("%d %b %Y"),
        size=report.size or "—",
        format=report.format,
        status=report.status,
    )


@router.get("/{report_id}/download", dependencies=[Depends(direction_roles)])
async def download_report(report_id: str, db: AsyncSession = Depends(get_db)):
    report = await db.get(GeneratedReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Rapport introuvable.")

    file_bytes = secure_document_storage.download_bytes(report.file_path)
    media_type = "application/pdf" if report.format.upper() == "PDF" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if report.format.upper() == "XLSX" else "text/csv"
    filename = f"{report.name.replace(' ', '_')}.{report.format.lower()}"
    return StreamingResponse(
        BytesIO(file_bytes),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

import csv
import json
from io import StringIO
from typing import List, Type
from datetime import datetime, timezone
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException
import logging

from app.schemas.employee import ErrorLine, ImportReport

logger = logging.getLogger(__name__)


def _parse_list_like(value):
    if value is None or isinstance(value, list):
        return value
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []
        if raw.startswith("["):
            try:
                parsed = json.loads(raw)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except json.JSONDecodeError:
                pass
        return [item.strip() for item in raw.split(",") if item.strip()]
    return value


def _parse_json_like(value):
    if value is None or isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        if raw.startswith("{") or raw.startswith("["):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return value
    return value

async def process_csv_import(
    file: UploadFile, 
    db: AsyncSession, 
    schema_class: Type[BaseModel], 
    model_class: Type,
    user_id: str,
    author_name: str,
    entity_type: str,
    unique_field: str = "id"
) -> ImportReport:
    """
    Fonction générique pour traiter l'import d'un fichier CSV.
    1. Lit le CSV.
    2. Valide chaque ligne selon le Pydantic `schema_class`.
    3. Rejette les lignes invalides avec rapport détaillé.
    4. Insère ou met à jour les données dans la base de données.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers CSV sont supportés.")
        
    content = await file.read()
    try:
        decoded_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Le fichier CSV doit être encodé en UTF-8.")
        
    reader = csv.DictReader(StringIO(decoded_content))
    
    processed_count = 0
    created_count = 0
    updated_count = 0
    errors: List[ErrorLine] = []
    
    valid_records = []
    
    # Identify date-only fields from schema (not datetime)
    from datetime import date as _date_type
    import typing
    _date_only_fields = set()
    for field_name, field_info in schema_class.model_fields.items():
        annotation = field_info.annotation
        # Unwrap Optional[X] → X
        origin = getattr(annotation, '__origin__', None)
        if origin is type(None) or str(origin) == 'typing.Union':
            args = getattr(annotation, '__args__', ())
            annotation = next((a for a in args if a is not type(None)), annotation)
        if annotation is _date_type:
            _date_only_fields.add(field_name)

    # 1. Parsing & Validation
    for line_num, row in enumerate(reader, start=2): # Start at 2 because line 1 is header
        processed_count += 1
        
        # Replace empty strings with None to allow validation rules to pass
        cleaned_row = {k: (v if v.strip() != "" else None) for k, v in row.items()}

        # Normalize date fields: strip time component from ISO-8601 timestamps
        for date_field in _date_only_fields:
            val = cleaned_row.get(date_field)
            if val and isinstance(val, str) and "T" in val:
                cleaned_row[date_field] = val.split("T")[0]
        
        try:
            validated_data = schema_class(**cleaned_row)
            record = validated_data.model_dump()
            for list_field in ["required_skill_ids", "mandatory_for_roles"]:
                if list_field in record:
                    record[list_field] = _parse_list_like(record[list_field])
            for json_field in ["source_signals"]:
                if json_field in record:
                    record[json_field] = _parse_json_like(record[json_field])
            valid_records.append((line_num, record))
        except ValidationError as e:
            error_details = []
            for err in e.errors():
                field = ".".join([str(x) for x in err["loc"]])
                error_details.append(f"{field}: {err['msg']}")
                
            errors.append(ErrorLine(line=line_num, error=" | ".join(error_details)))
            
    from sqlalchemy.exc import IntegrityError
    import copy

    # 2. Insertion / Upsertion in DB with Row-level Savepoints
    for line_num, record in valid_records:
        async def attempt_upsert(data_dict):
            nonlocal created_count, updated_count
            primary_key_val = data_dict.get(unique_field)
            if primary_key_val:
                db_item = await db.get(model_class, primary_key_val)
                if db_item:
                    for k, v in data_dict.items():
                        setattr(db_item, k, v)
                    updated_count += 1
                else:
                    new_item = model_class(**data_dict)
                    db.add(new_item)
                    created_count += 1
            else:
                new_item = model_class(**data_dict)
                db.add(new_item)
                created_count += 1
            await db.flush()

        # First attempt
        try:
            async with db.begin_nested():
                await attempt_upsert(record)
        except IntegrityError as e:
            if record.get(unique_field) and await db.get(model_class, record.get(unique_field)):
                updated_count -= 1
            else:
                created_count -= 1
            
            # Message clair sur la dépendance manquante
            error_msg = str(e)
            if "ForeignKeyViolationError" in error_msg or "foreign key constraint" in error_msg.lower():
                errors.append(ErrorLine(line=line_num, error="Échec d'intégrité (clé étrangère). Dépendance introuvable. Importez d'abord les entités parentes (départements, etc.)."))
            else:
                errors.append(ErrorLine(line=line_num, error="Erreur d'intégrité SQL (ex: clé étrangère introuvable)."))
        except Exception as e:
            if record.get(unique_field) and await db.get(model_class, record.get(unique_field)):
                updated_count -= 1
            else:
                created_count -= 1
            errors.append(ErrorLine(line=line_num, error=f"Database insertion error: {str(e)}"))

    # Commit only if there are valid records or we want to save history
    from app.models.domain import ImportHistory

    if created_count > 0 or updated_count > 0:
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Transaction commit failed: {str(e)}")

    # Enregistrer l'historique
    status_val = "success"
    if len(errors) > 0:
        status_val = "warning" if (created_count > 0 or updated_count > 0) else "error"

    report_dict = ImportReport(
        processed=processed_count,
        created=max(0, created_count),
        updated=max(0, updated_count),
        errors=errors
    ).model_dump()

    history = ImportHistory(
        filename=file.filename,
        entity_type=entity_type,
        author_name=author_name,
        processed_lines=processed_count,
        created_lines=max(0, created_count),
        updated_lines=max(0, updated_count),
        error_count=len(errors),
        status=status_val,
        full_report=report_dict,
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
    )
    
    db.add(history)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to save import history: {e}")

    if model_class.__name__ == "Employee":
        from sqlalchemy import select
        from app.models.domain import Employee
        from app.services.employee_identity_service import sync_employee_identity
        
        # Read the auto_provision setting
        from app.routers.admin import _read_keycloak_settings
        settings = _read_keycloak_settings()
        if settings.get("auto_provision", False):
            emails = [record.get("email") for _, record in valid_records if record.get("email")]
            if emails:
                result = await db.execute(select(Employee.id).where(Employee.email.in_(emails)))
                for employee_id, in result.all():
                    try:
                        await sync_employee_identity(employee_id, db)
                    except Exception as exc:
                        logger.warning("Provisioning Keycloak ignoré pour %s: %s", employee_id, exc)

    return ImportReport(**report_dict)

import csv
from io import StringIO
from typing import List, Dict, Type
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException
import logging

from app.schemas.employee import ErrorLine, ImportReport

logger = logging.getLogger(__name__)

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
    
    # 1. Parsing & Validation
    for line_num, row in enumerate(reader, start=2): # Start at 2 because line 1 is header
        processed_count += 1
        
        # Replace empty strings with None to allow validation rules to pass
        cleaned_row = {k: (v if v.strip() != "" else None) for k, v in row.items()}
        
        try:
            validated_data = schema_class(**cleaned_row)
            valid_records.append((line_num, validated_data.model_dump()))
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
            # Possible Foreign Key violation. Attempt fallback by removing foreign keys
            fallback_record = copy.deepcopy(record)
            fks_removed = []
            for k in list(fallback_record.keys()):
                if k.endswith("_id") and k != "id" and fallback_record[k] is not None:
                    fallback_record[k] = None
                    fks_removed.append(k)
            
            if fks_removed:
                try:
                    async with db.begin_nested():
                        # We must rollback the created/updated counts from the failed attempt
                        # Actually they were incremented in the failed transaction, so we should 
                        # technically decrement them, but it's simpler to just let attempt_upsert run again.
                        # Wait, the counters were incremented locally before flush threw an error!
                        # Let's adjust counts safely:
                        if record.get(unique_field) and await db.get(model_class, record.get(unique_field)):
                            updated_count -= 1
                        else:
                            created_count -= 1
                        
                        await attempt_upsert(fallback_record)
                        errors.append(ErrorLine(line=line_num, error=f"Importé partiellement sans les liaisons ({', '.join(fks_removed)}). Dépendances introuvables. Veuillez réimporter après avoir importé les données parentes."))
                except Exception as e2:
                    if fallback_record.get(unique_field) and await db.get(model_class, fallback_record.get(unique_field)):
                        updated_count -= 1
                    else:
                        created_count -= 1
                    errors.append(ErrorLine(line=line_num, error="Erreur base de données (après tentative de récupération)."))
            else:
                if record.get(unique_field) and await db.get(model_class, record.get(unique_field)):
                    updated_count -= 1
                else:
                    created_count -= 1
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
        user_id=user_id
    )
    
    db.add(history)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to save import history: {e}")

    return ImportReport(**report_dict)

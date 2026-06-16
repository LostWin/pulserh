from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.domain import NotificationConfig, UserPreference
from app.schemas.auth import CurrentUser
from app.schemas.user_settings import AvatarUploadResponse, PasswordActionResponse, UserSettingsResponse, UserSettingsUpdate

router = APIRouter(prefix="/users/me", tags=["User Settings"])


async def _get_or_create_settings(current_user: CurrentUser, db: AsyncSession) -> tuple[UserPreference, NotificationConfig]:
    pref_result = await db.execute(select(UserPreference).filter(UserPreference.user_id == current_user.id))
    pref = pref_result.scalar_one_or_none()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)

    notif_result = await db.execute(select(NotificationConfig).filter(NotificationConfig.user_id == current_user.id))
    notif = notif_result.scalar_one_or_none()
    if not notif:
        notif = NotificationConfig(user_id=current_user.id)
        db.add(notif)

    await db.commit()
    await db.refresh(pref)
    await db.refresh(notif)
    return pref, notif


@router.get("/settings", response_model=UserSettingsResponse)
async def get_my_settings(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pref, notif = await _get_or_create_settings(current_user, db)
    return UserSettingsResponse(
        theme=pref.theme,
        locale=pref.locale,
        timezone=pref.timezone,
        digest_frequency=pref.digest_frequency,
        avatar_data_url=pref.avatar_data_url,
        profile_title=pref.profile_title,
        birth_date_label=pref.birth_date_label,
        address_label=pref.address_label,
        work_location_label=pref.work_location_label,
        email_enabled=notif.email_enabled,
        in_app_enabled=notif.in_app_enabled,
        slack_enabled=notif.slack_enabled,
    )


@router.put("/settings", response_model=UserSettingsResponse)
async def update_my_settings(
    payload: UserSettingsUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pref, notif = await _get_or_create_settings(current_user, db)
    for field in ["theme", "locale", "timezone", "digest_frequency", "profile_title", "birth_date_label", "address_label", "work_location_label"]:
        value = getattr(payload, field)
        if value is not None:
            setattr(pref, field, value)
    for field in ["email_enabled", "in_app_enabled", "slack_enabled"]:
        value = getattr(payload, field)
        if value is not None:
            setattr(notif, field, value)
    await db.commit()
    await db.refresh(pref)
    await db.refresh(notif)
    return UserSettingsResponse(
        theme=pref.theme,
        locale=pref.locale,
        timezone=pref.timezone,
        digest_frequency=pref.digest_frequency,
        avatar_data_url=pref.avatar_data_url,
        profile_title=pref.profile_title,
        birth_date_label=pref.birth_date_label,
        address_label=pref.address_label,
        work_location_label=pref.work_location_label,
        email_enabled=notif.email_enabled,
        in_app_enabled=notif.in_app_enabled,
        slack_enabled=notif.slack_enabled,
    )


@router.post("/avatar", response_model=AvatarUploadResponse)
async def upload_my_avatar(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image.")
    content = await file.read()
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="L'image ne doit pas dépasser 2 Mo.")

    import base64

    pref, _ = await _get_or_create_settings(current_user, db)
    pref.avatar_data_url = f"data:{file.content_type};base64,{base64.b64encode(content).decode('ascii')}"
    await db.commit()
    await db.refresh(pref)
    return AvatarUploadResponse(avatar_data_url=pref.avatar_data_url)


@router.get("/password-action", response_model=PasswordActionResponse)
async def get_password_action():
    return PasswordActionResponse(redirect_hint="Utiliser Keycloak avec l'action UPDATE_PASSWORD.")

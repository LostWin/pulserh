from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class KeycloakAdminService:
    def __init__(self) -> None:
        self.base_url = settings.KEYCLOAK_INTERNAL_URL.rstrip("/")
        self.realm = settings.KEYCLOAK_REALM
        self.admin_realm = settings.KEYCLOAK_ADMIN_REALM
        self.client_id = settings.KEYCLOAK_ADMIN_CLIENT_ID
        self.username = settings.KEYCLOAK_ADMIN_USERNAME
        self.password = settings.KEYCLOAK_ADMIN_PASSWORD
        self.default_password = settings.KEYCLOAK_DEFAULT_PASSWORD
        self.required_action = settings.KEYCLOAK_DEFAULT_REQUIRED_ACTION

    async def _get_token(self) -> str:
        token_url = f"{self.base_url}/realms/{self.admin_realm}/protocol/openid-connect/token"
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                token_url,
                data={
                    "grant_type": "password",
                    "client_id": self.client_id,
                    "username": self.username,
                    "password": self.password,
                },
            )
            response.raise_for_status()
            return response.json()["access_token"]

    async def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        token = await self._get_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        headers.setdefault("Content-Type", "application/json")
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.request(method, url, headers=headers, **kwargs)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"Keycloak API Error: {e.response.text}")
                raise
            return response

    async def list_users(self) -> list[dict[str, Any]]:
        response = await self._request("GET", f"/admin/realms/{self.realm}/users?max=200")
        return response.json()

    async def find_user_by_email(self, email: str) -> dict[str, Any] | None:
        response = await self._request("GET", f"/admin/realms/{self.realm}/users?email={email}")
        users = response.json()
        return users[0] if users else None

    async def find_user_by_id(self, user_id: str) -> dict[str, Any]:
        response = await self._request("GET", f"/admin/realms/{self.realm}/users/{user_id}")
        return response.json()

    async def create_or_update_user(
        self,
        *,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        role: str,
        enabled: bool = True,
        temporary_password: str | None = None,
    ) -> dict[str, Any]:
        existing = await self.find_user_by_email(email)
        if existing:
            payload = {
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "enabled": enabled,
                "emailVerified": True,
            }
            await self._request("PUT", f"/admin/realms/{self.realm}/users/{existing['id']}", json=payload)
            user_id = existing["id"]
        else:
            payload = {
                "username": username,
                "email": email,
                "firstName": first_name,
                "lastName": last_name,
                "enabled": enabled,
                "emailVerified": True,
                "requiredActions": [self.required_action],
            }
            response = await self._request("POST", f"/admin/realms/{self.realm}/users", json=payload)
            location = response.headers.get("Location", "")
            user_id = location.rstrip("/").split("/")[-1]
            await self.set_password(user_id, temporary_password or self.default_password, temporary=True)
        await self.assign_realm_roles(user_id, [role])
        return await self.find_user_by_id(user_id)

    async def assign_realm_roles(self, user_id: str, roles: list[str]) -> None:
        current_roles = await self._request("GET", f"/admin/realms/{self.realm}/users/{user_id}/role-mappings/realm")
        current_names = {role["name"] for role in current_roles.json()}

        to_add = []
        for role_name in roles:
            role_response = await self._request("GET", f"/admin/realms/{self.realm}/roles/{role_name}")
            role_repr = role_response.json()
            to_add.append(role_repr)

        to_remove = []
        for role_name in ["collaborator", "manager", "hr", "director", "admin"]:
            if role_name in current_names and role_name not in roles:
                role_response = await self._request("GET", f"/admin/realms/{self.realm}/roles/{role_name}")
                to_remove.append(role_response.json())

        if to_remove:
            await self._request("DELETE", f"/admin/realms/{self.realm}/users/{user_id}/role-mappings/realm", json=to_remove)
        if to_add:
            await self._request("POST", f"/admin/realms/{self.realm}/users/{user_id}/role-mappings/realm", json=to_add)

    async def set_password(self, user_id: str, password: str, temporary: bool = True) -> None:
        await self._request(
            "PUT",
            f"/admin/realms/{self.realm}/users/{user_id}/reset-password",
            json={"type": "password", "temporary": temporary, "value": password},
        )

    async def set_enabled(self, user_id: str, enabled: bool) -> dict[str, Any]:
        user = await self.find_user_by_id(user_id)
        user["enabled"] = enabled
        await self._request("PUT", f"/admin/realms/{self.realm}/users/{user_id}", json=user)
        return await self.find_user_by_id(user_id)


keycloak_admin_service = KeycloakAdminService()

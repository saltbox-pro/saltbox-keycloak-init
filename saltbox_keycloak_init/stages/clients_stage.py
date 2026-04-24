import json
from pathlib import Path
from typing import Any

import aiofiles

from saltbox_keycloak_init.config import Settings
from saltbox_keycloak_init.manage.client_manager import ClientManager
from saltbox_keycloak_init.schema.client_schema import (
    GRAFANA_ROLE_TO_DESC,
    SALTBOX_ROLE_TO_DESC,
    Client,
    ClientRole,
)

BASE_DIR = Path(__file__).resolve().parent.parent
PATH_TO_RABBITMQ_CLIENT_CONFIG = BASE_DIR / 'client.d' / 'rabbitmq_client.json'
PATH_TO_GRAFANA_CLIENT_CONFIG = BASE_DIR / 'client.d' / 'grafana_client.json'
PATH_TO_SALTBOX_CORE_CLIENT_CONFIG = BASE_DIR / 'client.d' / 'saltbox_core_client.json'


async def _load_client_config(path: Path) -> dict[str, Any]:
    async with aiofiles.open(path) as f:
        payload = await f.read()
        return json.loads(payload)


async def _build_client(
    *,
    client_id: str,
    secret: str,
    path_to_config: Path,
    role_to_desc: dict[str, str]
) -> Client:
    config = await _load_client_config(path_to_config)
    roles: list[ClientRole] = []
    for r_name, r_desc in role_to_desc.items():
        role = ClientRole(r_name, r_desc)
        roles.append(role)

    return Client(
        client_id=client_id,
        secret=secret,
        config=config,
        roles=roles
    )


async def setup_clients(
    *,
    client_mgr: ClientManager,
    settings: Settings,
) -> tuple[str, str | None]:

    saltbox_client_id = settings.keycloak_client
    saltbox_secret = await settings.keycloak_client_saltbox_core_secret_meta.value
    saltbox_client = await _build_client(
        client_id=saltbox_client_id,
        secret=saltbox_secret,
        path_to_config=PATH_TO_SALTBOX_CORE_CLIENT_CONFIG,
        role_to_desc=SALTBOX_ROLE_TO_DESC
    )
    saltbox_uuid = await client_mgr.ensure_client(saltbox_client)
    await client_mgr.ensure_client_roles(client_uuid=saltbox_uuid, roles=saltbox_client.roles)

    grafana_client_id = settings.keycloak_client_grafana
    grafana_uuid: str | None = None
    grafana_secret = await settings.keycloak_client_grafana_secret_meta.value
    if grafana_secret:
        grafana_client = await _build_client(
            client_id=grafana_client_id,
            secret=grafana_secret,
            path_to_config=PATH_TO_GRAFANA_CLIENT_CONFIG,
            role_to_desc=GRAFANA_ROLE_TO_DESC
        )
        grafana_uuid = await client_mgr.ensure_client(grafana_client)
        await client_mgr.ensure_client_roles(client_uuid=grafana_uuid, roles=grafana_client.roles)

    return saltbox_uuid, grafana_uuid

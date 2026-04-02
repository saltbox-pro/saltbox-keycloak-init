import json
from typing import Any

import aiofiles

from saltbox_keycloak_init.config import Settings
from saltbox_keycloak_init.manage.client_manager import ClientManager
from saltbox_keycloak_init.schema.client_schema import GRAFANA_ADMIN_ROLE, Client, ClientRole

PATH_TO_GRAFANA_CLIENT_CONFIG = 'saltbox_keycloak_init/client.d/grafana_client.json'
PATH_TO_SALTBOX_CORE_CLIENT_CONFIG = 'saltbox_keycloak_init/client.d/saltbox_core_client.json'


async def _load_client_config(path: str) -> dict[str, Any]:
    async with aiofiles.open(path) as f:
        payload = await f.read()
        return json.loads(payload)


async def _build_saltbox_client(settings: Settings) -> Client:
    config = await _load_client_config(PATH_TO_SALTBOX_CORE_CLIENT_CONFIG)
    return Client(
        client_id=settings.keycloak_client,
        secret=settings.keycloak_client_saltbox_core_password,
        config=config,
        roles=[
            ClientRole(
                name='collections_admin', description='Collections admin role'),
            ClientRole(
                name='saltbox_admin', description='Salt.Box admin role'),
            ClientRole(
                name='tasks_admin', description='Tasks admin role'),
            ClientRole(
                name='jobs_admin', description='Jobs admin role'),
            ClientRole(
                name='test_common', description='Test common role'),
            ClientRole(
                name='masters_admin', description='Masters admin role'),
            ClientRole(
                name='scheduler_admin', description='Scheduler admin role'),
        ],
    )


async def _build_grafana_client(settings: Settings) -> Client:
    config = await _load_client_config(PATH_TO_GRAFANA_CLIENT_CONFIG)
    return Client(
        client_id=settings.grafana_client,
        secret=settings.keycloak_client_grafana_password,
        config=config,
        roles=[ClientRole(
            name=GRAFANA_ADMIN_ROLE, description='Grafana admin role')],
    )


async def setup_clients(
    client_mgr: ClientManager,
    settings: Settings,
) -> tuple[str, str | None]:

    saltbox_client = await _build_saltbox_client(settings)
    saltbox_uuid = await client_mgr.ensure_client(saltbox_client)
    await client_mgr.ensure_client_roles(saltbox_uuid, saltbox_client.roles)

    grafana_uuid: str | None = None
    if settings.grafana_client and settings.keycloak_client_grafana_password:
        grafana_client = await _build_grafana_client(settings)
        grafana_uuid = await client_mgr.ensure_client(grafana_client)
        await client_mgr.ensure_client_roles(grafana_uuid, grafana_client.roles)

    return saltbox_uuid, grafana_uuid

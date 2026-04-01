from saltbox_keycloak_init.config import Settings
from saltbox_keycloak_init.manage.client_manager import ClientManager
from saltbox_keycloak_init.schema.client_configs import GRAFANA_CLIENT_CONFIG, SALTBOX_CLIENT_CONFIG
from saltbox_keycloak_init.schema.client_schema import GRAFANA_ADMIN_ROLE, Client, ClientRole


def build_saltbox_client(settings: Settings) -> Client:
    return Client(
        client_id=settings.keycloak_client,
        secret=settings.keycloak_client_saltbox_core_password,
        config=SALTBOX_CLIENT_CONFIG,
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


def build_grafana_client(settings: Settings) -> Client:
    return Client(
        client_id=settings.grafana_client,
        secret=settings.keycloak_client_grafana_password,
        config=GRAFANA_CLIENT_CONFIG,
        roles=[ClientRole(
            name=GRAFANA_ADMIN_ROLE, description='Grafana admin role')],
    )


async def setup_clients(
    client_mgr: ClientManager,
    settings: Settings,
) -> tuple[str, str | None]:

    saltbox_client = build_saltbox_client(settings)
    saltbox_uuid = await client_mgr.ensure_client(saltbox_client)
    await client_mgr.ensure_client_roles(saltbox_uuid, saltbox_client.roles)

    grafana_uuid: str | None = None
    if settings.grafana_client and settings.keycloak_client_grafana_password:
        grafana_client = build_grafana_client(settings)
        grafana_uuid = await client_mgr.ensure_client(grafana_client)
        await client_mgr.ensure_client_roles(grafana_uuid, grafana_client.roles)

    return saltbox_uuid, grafana_uuid

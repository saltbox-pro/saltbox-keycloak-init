import asyncio

from keycloak import KeycloakAdmin, KeycloakError

from saltbox_keycloak_init.config import logger
from saltbox_keycloak_init.schema.client_schema import GRAFANA_ADMIN_ROLE, SALTBOX_ADMIN_ROLES
from saltbox_keycloak_init.utils import verify_client_roles


async def verify_roles(
    admin: KeycloakAdmin,
    realm_name: str,
    admin_name: str,
    saltbox_uuid: str,
    grafana_uuid: str | None,
) -> None:

    tasks = [verify_client_roles(
        admin,
        realm_name,
        admin_name,
        saltbox_uuid,
        SALTBOX_ADMIN_ROLES
    )]
    if grafana_uuid:
        tasks.append(verify_client_roles(
            admin,
            realm_name,
            admin_name,
            grafana_uuid,
            [GRAFANA_ADMIN_ROLE]
        ))

    is_verified = await asyncio.gather(*tasks)
    if not all(is_verified):
        msg = 'Roles verification failed'
        raise KeycloakError(msg)

    logger.info('Roles verification passed')

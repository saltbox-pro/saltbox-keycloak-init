import asyncio

from keycloak import KeycloakError

from saltbox_keycloak_init.config import logger
from saltbox_keycloak_init.schema.client_schema import GRAFANA_ADMIN_ROLE, SALTBOX_ADMIN_ROLES
from saltbox_keycloak_init.utils import verify_client_roles


async def verify_roles(
    admin_name: str,
    saltbox_uuid: str,
    grafana_uuid: str | None,
) -> None:
    
    verify_sb_task = verify_client_roles(
        admin_name,
        saltbox_uuid,
        SALTBOX_ADMIN_ROLES
    )
    verify_grafana_task = verify_client_roles(
        admin_name,
        grafana_uuid,
        [GRAFANA_ADMIN_ROLE]
    )
    is_verified = await asyncio.gather(verify_sb_task, verify_grafana_task)
    if not is_verified:
        msg = 'Role verification failed'
        raise KeycloakError(msg)

    msg = 'Role verification passed'
    logger.info(msg)
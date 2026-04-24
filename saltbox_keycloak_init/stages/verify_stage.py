import asyncio

from keycloak import KeycloakAdmin, KeycloakError

from saltbox_keycloak_init.config import logger
from saltbox_keycloak_init.schema.client_schema import GRAFANA_ROLE_TO_DESC, SALTBOX_ROLE_TO_DESC
from saltbox_keycloak_init.utils import verify_client_roles


async def verify_roles(
    *,
    admin: KeycloakAdmin,
    realm_name: str,
    admin_name: str,
    saltbox_uuid: str,
    grafana_uuid: str | None,
) -> None:

    tasks = [
        verify_client_roles(
            admin=admin,
            realm_name=realm_name,
            username=admin_name,
            client_uuid=saltbox_uuid,
            expected_roles=list(SALTBOX_ROLE_TO_DESC)
        ),
    ]
    if grafana_uuid:
        tasks.append(verify_client_roles(
            admin=admin,
            realm_name=realm_name,
            username=admin_name,
            client_uuid=grafana_uuid,
            expected_roles=list(GRAFANA_ROLE_TO_DESC)
        ))

    is_verified = await asyncio.gather(*tasks)
    if not all(is_verified):
        msg = 'Roles verification failed'
        raise KeycloakError(msg)

    logger.info('Roles verification passed')

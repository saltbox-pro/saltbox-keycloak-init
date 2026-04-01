import asyncio

from keycloak import KeycloakAdmin, KeycloakAuthenticationError

from saltbox_keycloak_init.config import SETTINGS, logger
from saltbox_keycloak_init.manage.client_manager import ClientManager
from saltbox_keycloak_init.manage.user_manager import UserManager
from saltbox_keycloak_init.stages.clients_stage import setup_clients
from saltbox_keycloak_init.stages.user_stage import setup_users
from saltbox_keycloak_init.stages.verify_stage import verify_roles


async def create_user_realm() -> KeycloakAdmin:
    master_realm = KeycloakAdmin(
        server_url=SETTINGS.keycloak_url.rstrip('/') + '/',
        username='admin',
        password=SETTINGS.keycloak_admin_password,
        realm_name='master',
        verify=True,
    )
    realm_representations = await master_realm.a_get_realms()
    realm_names = [r['realm'] for r in realm_representations]

    expected_realm = SETTINGS.keycloak_realm
    if expected_realm not in realm_names:
        logger.info(f'Realm {expected_realm!r} created')
        await master_realm.a_create_realm({
            "realm": SETTINGS.keycloak_realm, "enabled": True},
            skip_exists=True
        )
    else:
        logger.info(f'Realm {expected_realm!r} already exist')

    master_realm.connection.realm_name = SETTINGS.keycloak_realm
    return master_realm


async def init() -> None:

    user_realm = await create_user_realm()

    client_manager = ClientManager(user_realm, SETTINGS)
    saltbox_uuid, grafana_uuid = await setup_clients(client_manager, SETTINGS)

    user_manager = UserManager(user_realm, SETTINGS)
    await setup_users(
        user_manager,
        SETTINGS,
        saltbox_uuid,
        grafana_uuid
    )
    await client_manager.update_direct_access(saltbox_uuid, SETTINGS.keycloak_client_direct_access)

    if SETTINGS.keycloak_strict_role_check:
        await verify_roles(
            user_realm,
            SETTINGS.keycloak_realm,
            SETTINGS.keycloak_admin_name,
            saltbox_uuid,
            grafana_uuid
        )


async def init_with_retry(retries: int = 10, delay: float = 5.0) -> None:
    for attempt in range(1, retries + 1):
        try:
            await init()
            return
        except KeycloakAuthenticationError as ex:
            if attempt == retries:
                raise

            msg = (
                f'Attempt {attempt}/{retries} failed: {ex}. ' +
                f'Retrying in {delay} sec ...'
            )
            logger.warning(msg)
            await asyncio.sleep(delay)


def main() -> None:
    logger.info('======= Starting Keycloak initialization =======')
    asyncio.run(init_with_retry())
    logger.info('======= Keycloak initialization completed =======')

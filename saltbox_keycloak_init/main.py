import asyncio

from keycloak import KeycloakAdmin, KeycloakAuthenticationError, KeycloakPostError, KeycloakConnectionError

from saltbox_keycloak_init.config import SETTINGS, logger
from saltbox_keycloak_init.manage.client_manager import ClientManager
from saltbox_keycloak_init.manage.user_manager import UserManager
from saltbox_keycloak_init.stages.clients_stage import setup_clients
from saltbox_keycloak_init.stages.user_stage import setup_users
from saltbox_keycloak_init.stages.verify_stage import verify_roles


async def create_user_realm() -> KeycloakAdmin:
    admin_password = await SETTINGS.keycloak_admin_secret_meta.value
    master_realm = KeycloakAdmin(
        server_url=SETTINGS.keycloak_url.rstrip('/') + '/',
        username='admin',
        password=admin_password,
        realm_name='master',
        verify=True,
    )
    realm_representations = await master_realm.a_get_realms()
    realm_names = [r['realm'] for r in realm_representations]

    expected_realm = SETTINGS.keycloak_realm
    if expected_realm not in realm_names:
        logger.info(f'Realm {expected_realm!r} created')
        sup_loc = [i.strip() for i in SETTINGS.keycloak_supported_locales.split(',')]
        realm_payload = {
            'realm': SETTINGS.keycloak_realm,
            'enabled': True,
            'loginTheme': SETTINGS.keycloak_login_theme,
            'internationalizationEnabled': True,
            'supportedLocales': sup_loc,
            'defaultLocale': SETTINGS.keycloak_default_locale,
        }
        await master_realm.a_create_realm(realm_payload, skip_exists=True)
        brute_force_payload = {
            **realm_payload,
            'bruteForceProtected': True,
            'failureFactor': SETTINGS.keycloak_bf_failure_factor,
            'maxDeltaTimeSeconds': SETTINGS.keycloak_bf_max_delta_time_sc,
            'maxFailureWaitSeconds': SETTINGS.keycloak_bf_max_failure_wait_sc,
            'waitIncrementSeconds': SETTINGS.keycloak_bf_wait_increment_sc,
            'minimumQuickLoginWaitSeconds': SETTINGS.keycloak_bf_min_quick_login_wait_sc,
            'quickLoginCheckMilliSeconds': SETTINGS.keycloak_bf_quick_login_check_msc,
        }
        await master_realm.a_update_realm(expected_realm, brute_force_payload)
    else:
        logger.info(f'Realm {expected_realm!r} already exist')

    master_realm.connection.realm_name = SETTINGS.keycloak_realm
    return master_realm


async def init() -> None:

    user_realm = await create_user_realm()
    client_manager = ClientManager(user_realm, SETTINGS)
    saltbox_uuid, grafana_uuid = await setup_clients(client_mgr=client_manager, settings=SETTINGS)

    user_manager = UserManager(user_realm, SETTINGS)
    await setup_users(
        user_mgr=user_manager,
        settings=SETTINGS,
        saltbox_uuid=saltbox_uuid,
        grafana_uuid=grafana_uuid
    )
    await client_manager.update_direct_access(client_uuid=saltbox_uuid, enabled=SETTINGS.keycloak_client_direct_access)

    if SETTINGS.keycloak_strict_role_check:
        await verify_roles(
            admin=user_realm,
            realm_name=SETTINGS.keycloak_realm,
            admin_name=SETTINGS.keycloak_admin_name,
            saltbox_uuid=saltbox_uuid,
            grafana_uuid=grafana_uuid,
        )


async def init_with_retry(retries: int = 30, delay: float = 5.0) -> None:
    for attempt in range(1, retries + 1):
        try:
            await init()
            return
        except KeycloakConnectionError as ex:
            if attempt == retries:
                raise

            msg = (
                f'Keycloak is unavailable: {ex}. ' +
                f'Retry in {delay} sec'
            )
            logger.warning(msg)
            await asyncio.sleep(delay)

        except KeycloakPostError as ex:
            if ex.response_code == 503:
                if attempt == retries:
                    raise

                msg = (
                    f'Keycloak bootstrap is in progress. ' +
                    f'Retry in {delay} sec...'
                )
                logger.info(msg)
                await asyncio.sleep(delay)

        except KeycloakAuthenticationError as ex:
            if attempt == retries:
                raise

            msg = (
                f'Keycloak authentication failed: {ex}. ' +
                f'Retrying in {delay} sec...'
            )
            logger.warning(msg)
            await asyncio.sleep(delay)
        
        except Exception as ex:
            msg = (
                f'Attempt {attempt}/{retries} failed: {ex}. ' +
                f'Retrying in {delay} sec...'
            )
            logger.error(msg)
            await asyncio.sleep(delay)


def main() -> None:
    logger.info('======= Starting Keycloak initialization =======')
    asyncio.run(init_with_retry())
    logger.info('======= Keycloak initialization completed =======')

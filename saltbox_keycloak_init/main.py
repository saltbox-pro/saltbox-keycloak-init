import asyncio

from keycloak import KeycloakAdmin

from saltbox_keycloak_init.config import SETTINGS, Settings, logger
from saltbox_keycloak_init.manage.client_manager import ClientManager
from saltbox_keycloak_init.manage.realm_manager import RealmManager
from saltbox_keycloak_init.manage.user_manager import UserManager
from saltbox_keycloak_init.stages.clients_stage import setup_clients
from saltbox_keycloak_init.stages.user_stage import setup_users
from saltbox_keycloak_init.stages.verify_stage import verify_roles

def get_admin(settings: Settings) -> KeycloakAdmin:
    return KeycloakAdmin(
        server_url=settings.keycloak_url,
        username='admin',
        password=settings.keycloak_admin_password,
        realm_name='master',
        verify=True,
    )

async def init() -> None:
    
    admin = get_admin(SETTINGS)
    admin.realm_name = SETTINGS.keycloak_realm
    
    realm_manager = RealmManager(admin, SETTINGS)
    await realm_manager.ensure_realm()
    await realm_manager.enable_realm()

    client_manager = ClientManager(admin, SETTINGS)
    saltbox_uuid, grafana_uuid = await setup_clients(client_manager, SETTINGS)
    
    user_manager = UserManager(admin, SETTINGS)
    await setup_users(
        user_manager,
        SETTINGS,
        saltbox_uuid,
        grafana_uuid
    )
    
    await client_manager.update_direct_access(saltbox_uuid, SETTINGS.client_direct_access)
    
    if SETTINGS.strict_role_check:
        await verify_roles(SETTINGS, saltbox_uuid, grafana_uuid)


if __name__ == '__main__':
    logger.info('Starting Keycloak initialization')
    asyncio.run(init())
    logger.info('Keycloak initialization completed')

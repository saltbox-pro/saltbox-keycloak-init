from keycloak import KeycloakGetError

from saltbox_keycloak_init.config import logger
from saltbox_keycloak_init.manage.base_manager import BaseManager


class RealmManager(BaseManager):
    async def ensure_realm(self) -> None:
        realm_name = self.settings.keycloak_realm
        try:
            await self.admin.a_get_realm(realm_name)
            msg = f'Realm {realm_name!r} exists, disabling'
            logger.info(msg)
            await self.admin.a_update_realm(realm_name, {'enabled': False})
        except KeycloakGetError:
            await self._create_realm(realm_name)
    
    async def _create_realm(self, realm_name: str) -> None:
        msg = f'Realm {realm_name!r} does not exist, creating'
        logger.info(msg)
        
        payload = {'realm': realm_name, 'enabled': False}
        await self.admin.a_create_realm(payload)
    
    async def enable_realm(self) -> None:
        realm_name = self.settings.keycloak_realm
        msg = f'Enabling realm {realm_name!r}'
        logger.info(msg)
        await self.admin.a_update_realm(realm_name, {})
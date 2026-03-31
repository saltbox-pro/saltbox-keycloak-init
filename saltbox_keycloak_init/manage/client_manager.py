from keycloak import KeycloakGetError

from saltbox_keycloak_init.config import logger
from saltbox_keycloak_init.manage.base_manager import BaseManager
from saltbox_keycloak_init.schema.client_schema import Client, ClientRole


class ClientManager(BaseManager):
    async def ensure_client(self, client: Client) -> str:
        client_uuid = await self.admin.a_get_client_id(client.client_id)
        if client_uuid:
            msg = f'Client {client.client_id!r} already exists with UUID {client_uuid!r}'
            logger.info(msg)
            return client_uuid

        payload = {
            **client.config,
            'clientId': client.client_id,
            'secret': client.secret
        }
        await self.admin.a_create_client(payload, skip_exists=False)
        client_uuid = await self.admin.a_get_client_id(client.client_id)
        
        msg = f'Client {client.client_id!r} created with UUID {client_uuid!r}'
        logger.info(msg)

        return client_uuid

    async def ensure_client_roles(
        self,
        client_uuid: str,
        roles: list[ClientRole]
    ) -> None:
        for role in roles:
            try:
                await self.admin.a_get_client_role(client_uuid, role.name)
                msg = f'Role {role.name!r} already exists for client UUID {client_uuid!r}'
                logger.info(msg)
            except KeycloakGetError:
                await self._create_client_role(client_uuid, role)

    async def _create_client_role(
        self,
        client_uuid: str,
        role: ClientRole
    ) -> None:
        payload = {
            'name': role.name,
            'description': role.description
        }
        await self.admin.a_create_client_role(
            client_uuid,
            payload,
            skip_exists=False
        )
        msg = f'Role {role.name!r} created for client UUID {client_uuid!r}'
        logger.info(msg)
    
    async def update_direct_access(self, client_uuid: str, enabled: bool) -> None:
        msg = f'Setting directAccessGrantsEnabled={enabled!r} for client UUID {client_uuid!r}'
        logger.info(msg)
        await self.admin.a_update_client(client_uuid, {'directAccessGrantsEnabled': enabled})
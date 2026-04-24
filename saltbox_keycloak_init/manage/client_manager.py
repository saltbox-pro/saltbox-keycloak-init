from keycloak import KeycloakGetError

from saltbox_keycloak_init.config import logger
from saltbox_keycloak_init.manage.base_manager import BaseManager
from saltbox_keycloak_init.schema.client_schema import Client, ClientRole


class ClientManager(BaseManager):
    async def ensure_client(self, client: Client) -> str:
        client_uuid = await self.admin.a_get_client_id(client.client_id)
        if client_uuid:
            logger.info(f'Client {client.client_id!r} already exists with UUID {client_uuid!r}')
            return client_uuid

        payload = {
            **client.config,
            'clientId': client.client_id,
            'secret': client.secret
        }
        await self.admin.a_create_client(payload, skip_exists=False)
        client_uuid = await self.admin.a_get_client_id(client.client_id)
        if client_uuid is None:
            msg = f'Not found client UUID by {client.client_id!r} client name'
            raise KeycloakGetError(msg)

        logger.info(f'Client {client.client_id!r} created with UUID {client_uuid!r}')
        return client_uuid

    async def ensure_client_roles(
        self,
        *,
        client_uuid: str,
        roles: list[ClientRole]
    ) -> None:
        for role in roles:
            try:
                await self.admin.a_get_client_role(client_id=client_uuid, role_name=role.name)
                logger.info(f'Role {role.name!r} already exists for client UUID {client_uuid!r}')
            except KeycloakGetError:
                await self._create_client_role(client_uuid=client_uuid, role=role)

    async def _create_client_role(
        self,
        *,
        client_uuid: str,
        role: ClientRole
    ) -> None:
        payload = {
            'name': role.name,
            'description': role.description
        }
        await self.admin.a_create_client_role(
            client_role_id=client_uuid,
            payload=payload,
            skip_exists=False
        )
        logger.info(f'Role {role.name!r} created for client UUID {client_uuid!r}')

    async def update_direct_access(
        self,
        *,
        client_uuid: str,
        enabled: bool
    ) -> None:
        logger.info(f'Setting directAccessGrantsEnabled={enabled!r} for client UUID {client_uuid!r}')

        client_data = await self.admin.a_get_client(client_uuid)
        client_data['directAccessGrantsEnabled'] = enabled
        await self.admin.a_update_client(client_id=client_uuid, payload=client_data)

from saltbox_keycloak_init.config import logger
from saltbox_keycloak_init.manage.base_manager import BaseManager
from saltbox_keycloak_init.schema.user_schema import User


class UserManager(BaseManager):
    async def ensure_user(self, user: User) -> str:
        user_id = await self.admin.a_get_user_id(user.username)
        if user_id:
            msg = (
                f'User {user.username!r} already exists'
                f' in realm {self.settings.keycloak_realm!r} with id {user_id!r}'
            )
            logger.info(msg)
            return user_id

        user_id = await self.admin.a_create_user(
            {
                'username': user.username,
                'email': user.email,
                'firstName': user.first_name,
                'lastName': user.last_name,
                'enabled': True,
            },
            exist_ok=False,
        )
        await self.admin.a_set_user_password(user_id, password=user.password, temporary=False)
        logger.info(f'User {user.username!r} created in realm {self.settings.keycloak_realm!r}')

        return user_id

    async def assign_client_roles(
        self,
        user_id: str,
        client_uuid: str,
        role_names: list[str],
    ) -> None:
        for role_name in role_names:
            role_representation = await self.admin.a_get_client_role(client_uuid, role_name)
            await self.admin.a_assign_client_role(user_id, client_uuid, [role_representation])
            logger.info(f'Role {role_name!r} from client UUID {client_uuid!r} assigned to user {user_id!r}')

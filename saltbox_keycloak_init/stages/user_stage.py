from saltbox_keycloak_init.config import Settings
from saltbox_keycloak_init.manage.user_manager import UserManager
from saltbox_keycloak_init.schema.client_schema import GRAFANA_ROLE_TO_DESC, SALTBOX_ROLE_TO_DESC
from saltbox_keycloak_init.schema.user_schema import User


async def build_user(settings: Settings, password: str) -> User:
    return User(
        username=settings.keycloak_user_name,
        email=settings.keycloak_user_email,
        first_name=settings.keycloak_user_firstname,
        last_name=settings.keycloak_user_lastname,
        password=password,
    )


async def build_admin_user(settings: Settings, password: str) -> User:
    return User(
        username=settings.keycloak_admin_name,
        email=settings.keycloak_admin_email,
        first_name=settings.keycloak_admin_firstname,
        last_name=settings.keycloak_admin_lastname,
        password=password,
    )


async def setup_users(
    *,
    user_mgr: UserManager,
    settings: Settings,
    saltbox_uuid: str,
    grafana_uuid: str | None,
) -> None:

    if settings.keycloak_user_name:
        user_password = await settings.saltbox_user_secret_meta.value
        user = await build_user(settings, user_password)
        await user_mgr.ensure_user(user)

    if settings.keycloak_admin_name:
        admin_password = await settings.keycloak_saltbox_admin_secret_meta.value
        admin_user = await build_admin_user(settings, admin_password)
        admin_id = await user_mgr.ensure_user(admin_user)
        await user_mgr.assign_client_roles(
            user_id=admin_id,
            client_uuid=saltbox_uuid,
            role_names=list(SALTBOX_ROLE_TO_DESC)
        )
        if grafana_uuid:
            await user_mgr.assign_client_roles(
                user_id=admin_id,
                client_uuid=grafana_uuid,
                role_names=list(GRAFANA_ROLE_TO_DESC)
            )

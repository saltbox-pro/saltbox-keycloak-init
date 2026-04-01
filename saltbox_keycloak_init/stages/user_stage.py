from saltbox_keycloak_init.config import Settings
from saltbox_keycloak_init.manage.user_manager import UserManager
from saltbox_keycloak_init.schema.client_schema import GRAFANA_ADMIN_ROLE, SALTBOX_ADMIN_ROLES
from saltbox_keycloak_init.schema.user_schema import User


def build_user(settings: Settings) -> User:
    return User(
        username=settings.keycloak_user_name,
        email=settings.keycloak_user_email,
        first_name=settings.keycloak_user_firstname,
        last_name=settings.keycloak_user_lastname,
        password=settings.saltbox_user_password,
    )


def build_admin_user(settings: Settings) -> User:
    return User(
        username=settings.keycloak_admin_name,
        email=settings.keycloak_admin_email,
        first_name=settings.keycloak_admin_firstname,
        last_name=settings.keycloak_admin_lastname,
        password=settings.saltbox_admin_password,
    )


async def setup_users(
    user_mgr: UserManager,
    settings: Settings,
    saltbox_uuid: str,
    grafana_uuid: str | None,
) -> None:

    if settings.keycloak_user_name:
        await user_mgr.ensure_user(build_user(settings))

    if settings.keycloak_admin_name:
        admin_id = await user_mgr.ensure_user(build_admin_user(settings))
        await user_mgr.assign_client_roles(
            admin_id,
            saltbox_uuid,
            SALTBOX_ADMIN_ROLES
        )
        if grafana_uuid:
            await user_mgr.assign_client_roles(
                admin_id,
                grafana_uuid,
                [GRAFANA_ADMIN_ROLE]
            )

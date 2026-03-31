from keycloak import KeycloakAdmin

from saltbox_keycloak_init.config import logger

async def verify_client_roles(
    admin: KeycloakAdmin,
    realm_name: str,
    username: str,
    client_uuid: str,
    expected_roles: list[str],
) -> bool:
    if not expected_roles:
        msg = f'No expected roles for user {username!r} in client UUID {client_uuid!r}'
        logger.info(msg)
        return True

    user_id = await admin.a_get_user_id(username)
    if not user_id:
        msg = f'User {username!r} not found in realm {realm_name!r}'
        logger.error(msg)
        return False

    assigned = await admin.a_get_client_roles_of_user(user_id, client_uuid)
    assigned_names = {r['name'] for r in assigned}
    missing = set(expected_roles) - assigned_names

    if missing:
        sorted_missed = ", ".join(sorted(missing))
        msg = (
            f'Missing roles for user {username!r}'
            f' in client UUID {client_uuid!r}: {sorted_missed}'
        )
        logger.error(msg)
        return False

    msg = f'All expected roles assigned for user {username!r} in client UUID {client_uuid!r}'
    logger.info(msg)
    return True
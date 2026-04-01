from keycloak import KeycloakAdmin

from saltbox_keycloak_init.config import Settings


class BaseManager:  # noqa: B903
    def __init__(self, admin: KeycloakAdmin, settings: Settings):
        self.admin = admin
        self.settings = settings

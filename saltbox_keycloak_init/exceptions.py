class KeycloakInitError(Exception):
    msg: str = 'keycloak initialization failed'

    def __init__(self, msg: str | None = None) -> None:
        if msg is not None:
            self.msg = msg
        super().__init__(self.msg)


class AuthenticatorProviderNotFoundError(KeycloakInitError):
    msg = 'authenticator provider is not registered in keycloak'


class FlowExecutionNotFoundError(KeycloakInitError):
    msg = 'authentication flow execution not found'

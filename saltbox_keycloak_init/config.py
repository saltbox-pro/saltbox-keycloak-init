import dataclasses
import logging.config
import os
from typing import Any

import anyio


@dataclasses.dataclass(frozen=True)
class SecretMeta:
    name: str
    is_addon_module: bool = False
    base_dir: anyio.Path = '/run/secrets'  # type: ignore

    @property
    async def absolute_path(self) -> anyio.Path:
        return anyio.Path(f'{self.base_dir}/{self.name}')

    @property
    async def value(self) -> str:
        path = await self.absolute_path
        if await path.exists():
            trailing_secret = await path.read_text()
            return trailing_secret.rstrip('\n')
        if not self.is_addon_module:
            msg = f'Secret {path!r} not exist'
            raise ValueError(msg)
        return ''


class Settings:
    keycloak_url: str = ''
    keycloak_realm: str = ''
    keycloak_client: str = ''
    keycloak_admin_secret_meta: SecretMeta = SecretMeta('keycloak_admin_password')
    keycloak_client_saltbox_core_secret_meta: SecretMeta = SecretMeta('keycloak_client_saltbox_core_password')

    keycloak_client_grafana: str = ''
    keycloak_client_grafana_secret_meta: SecretMeta = SecretMeta(
        'keycloak_client_grafana_password', is_addon_module=True)

    keycloak_user_name: str = ''
    keycloak_user_email: str = ''
    keycloak_user_firstname: str = ''
    keycloak_user_lastname: str = ''
    saltbox_user_secret_meta: SecretMeta = SecretMeta('saltbox_user_password')

    keycloak_admin_name: str = ''
    keycloak_admin_email: str = ''
    keycloak_admin_firstname: str = ''
    keycloak_admin_lastname: str = ''
    keycloak_saltbox_admin_secret_meta: SecretMeta = SecretMeta('saltbox_admin_password')

    keycloak_client_direct_access: bool = False
    keycloak_strict_role_check: bool = True
    keycloak_init_log_level: str = 'INFO'

    def __init__(self) -> None:
        for field, field_type in self.__annotations__.items():
            field_to_uppercase = field.upper()
            raw_env = os.environ.get(field_to_uppercase)
            if raw_env is not None:
                env = self._cast_raw_env(raw_env, field_type)
                setattr(self, field, env)

    @classmethod
    def _cast_raw_env(cls, raw_value: str, value_type: type) -> Any:
        if value_type is bool:
            return raw_value.lower() == 'true'
        if value_type is int:
            return int(raw_value)
        return raw_value


SETTINGS: Settings = Settings()
_main_logger_name = __name__.split('.')[0]


LOG_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "format": "%(asctime)s | %(levelname)s [%(filename)s:%(lineno)d] %(message)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        _main_logger_name: {
            "handlers": ["default"],
            "level": SETTINGS.keycloak_init_log_level.upper(),
            "propagate": False,
        },
    },
}
logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger(name=_main_logger_name)

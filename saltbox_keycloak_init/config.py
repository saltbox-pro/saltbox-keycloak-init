import logging.config
import os
from pathlib import Path
from typing import Any

DOCKER_SECRETS_DIR = '/run/secrets'


class Settings:
    keycloak_url: str
    keycloak_realm: str
    keycloak_client: str
    keycloak_admin_password: str
    keycloak_client_saltbox_core_password: str

    keycloak_user_name: str = ''
    keycloak_user_email: str = ''
    keycloak_user_firstname: str = ''
    keycloak_user_lastname: str = ''
    saltbox_user_password: str = ''

    keycloak_admin_name: str = ''
    keycloak_admin_email: str = ''
    keycloak_admin_firstname: str = ''
    keycloak_admin_lastname: str = ''
    saltbox_admin_password: str = ''

    grafana_client: str = ''
    keycloak_client_grafana_password: str = ''

    keycloak_client_direct_access: bool = False
    keycloak_strict_role_check: bool = True

    keycloak_init_log_level: str = 'INFO'

    def __init__(self):
        for field, field_type in self.__annotations__.items():
            env = field.upper()
            raw_value = os.environ.get(env)
            if not raw_value:
                raw_value = self._extract_secret(field)

            if raw_value is None:
                msg = f'Missing required {env!r} env'
                raise ValueError(msg)
            else:
                value = self._cast_raw_env(raw_value, field_type)

            setattr(self, field, value)

    @staticmethod
    def _cast_raw_env(raw_value: str, value_type: type) -> Any:
        if value_type is bool:
            return raw_value.lower() == 'true'
        if value_type is int:
            return int(raw_value)
        return raw_value

    @staticmethod
    def _extract_secret(sub_path: str):
        path = Path(f'{DOCKER_SECRETS_DIR}/{ sub_path }')
        if path.exists():
            with Path.open(path) as f:
                return f.read().rstrip('\n')
        return None


SETTINGS = Settings()
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

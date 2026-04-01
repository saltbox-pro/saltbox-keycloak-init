import logging.config
from logging import _levelToName as LOG_LEVELS  # type: ignore
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


def validate_log_level(value: str) -> str:
    value = value.upper()
    if value not in LOG_LEVELS.values():
        msg = f'Unexpected log level: {value}'
        raise ValueError(msg)
    return value


LogLevelStr = Annotated[str, AfterValidator(validate_log_level)]


class Settings(BaseSettings):
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

    log_level: LogLevelStr = 'INFO'

    model_config = SettingsConfigDict(env_file='../.env', secrets_dir='/run/secrets', extra='ignore')


SETTINGS = Settings()
_main_logger_name = __name__.split('.')[0]


class LogConfig(BaseModel):
    level: LogLevelStr = SETTINGS.log_level
    version: int = 1
    formatters: dict[str, Any] = {
        'default': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '%(levelname)s [%(filename)s:%(lineno)d] %(message)s',
        },
    }
    handlers: dict[str, Any] = {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stderr',
        },
    }
    loggers: dict[str, Any] = {
        _main_logger_name: {
            'handlers': ['default'],
            'level': SETTINGS.log_level,
            'propagate': False,
        },
    }


LOG_CONFIG = LogConfig()
logging.config.dictConfig(LOG_CONFIG.model_dump())
logger = logging.getLogger(name=_main_logger_name)

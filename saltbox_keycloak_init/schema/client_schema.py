import dataclasses

GRAFANA_ADMIN_ROLE: str = 'grafana_admin'

SALTBOX_ADMIN_ROLES: list[str] = [
    'saltbox_admin',
    'collections_admin',
    'tasks_admin',
    'jobs_admin',
    'test_common',
    'masters_admin',
    'scheduler_admin'
]


@dataclasses.dataclass
class ClientRole:
    name: str
    description: str


@dataclasses.dataclass
class Client:
    client_id: str
    secret: str
    roles: list[ClientRole]
    config: dict[str, object]

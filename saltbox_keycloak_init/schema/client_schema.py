import dataclasses

GRAFANA_ROLE_TO_DESC: dict[str, str] = {
    'grafana_admin': 'Grafana admin role',
}

SALTBOX_ROLE_TO_DESC: dict[str, str] = {
    'saltbox_admin': 'Salt.Box admin role',
    'collections_admin': 'Collections admin role',
    'tasks_admin': 'Tasks admin role',
    'jobs_admin': 'Jobs admin role',
    'test_common': 'Test common role',
    'masters_admin': 'Masters admin role',
    'scheduler_admin': 'Scheduler admin role'
}


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

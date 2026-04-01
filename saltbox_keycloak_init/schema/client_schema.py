from pydantic import BaseModel

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


class ClientRole(BaseModel):
    name: str
    description: str


class Client(BaseModel):
    client_id: str
    secret: str
    roles: list[ClientRole]
    config: dict[str, object]

from pydantic import BaseModel

GRAFANA_ADMIN_ROLE = 'grafana_admin'

SALTBOX_ADMIN_ROLES: list[str] = [
	GRAFANA_ADMIN_ROLE,
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

from typing import Any

from saltbox_keycloak_init.config import logger
from saltbox_keycloak_init.exceptions import AuthenticatorProviderNotFoundError, FlowExecutionNotFoundError
from saltbox_keycloak_init.manage.base_manager import BaseManager


class FlowManager(BaseManager):
    async def ensure_provider_registered(self, provider_id: str) -> None:
        providers = await self.admin.a_get_authenticator_providers()
        provider_ids = {provider['id'] for provider in providers}
        if provider_id not in provider_ids:
            msg = f'authenticator provider {provider_id!r} is not registered in keycloak'
            raise AuthenticatorProviderNotFoundError(msg)

    async def ensure_flow_copy(self, *, source_alias: str, target_alias: str) -> None:
        flows = await self.admin.a_get_authentication_flows()
        if any(flow['alias'] == target_alias for flow in flows):
            logger.info(f'authentication flow {target_alias!r} already exists')
            return

        _ = await self.admin.a_copy_authentication_flow(payload={'newName': target_alias}, flow_alias=source_alias)
        logger.info(f'authentication flow {target_alias!r} copied from {source_alias!r}')

    async def replace_execution_provider(
        self,
        *,
        flow_alias: str,
        old_provider_id: str,
        new_provider_id: str,
    ) -> None:
        executions = await self.admin.a_get_authentication_flow_executions(flow_alias)
        old_execution = _find_execution(executions, old_provider_id)
        new_execution = _find_execution(executions, new_provider_id)

        if old_execution is None:
            if new_execution is None:
                msg = f'execution {old_provider_id!r} not found in authentication flow {flow_alias!r}'
                raise FlowExecutionNotFoundError(msg)
            logger.info(f'execution {new_provider_id!r} already set in authentication flow {flow_alias!r}')
            return

        parent_alias = await self._parent_flow_alias(executions, old_execution, flow_alias)
        if new_execution is None:
            _ = await self.admin.a_create_authentication_flow_execution(
                payload={'provider': new_provider_id},
                flow_alias=parent_alias,
            )
            logger.info(f'execution {new_provider_id!r} added to authentication flow {parent_alias!r}')
            executions = await self.admin.a_get_authentication_flow_executions(flow_alias)
            new_execution = _find_execution(executions, new_provider_id)
            if new_execution is None:
                msg = f'execution {new_provider_id!r} not found in authentication flow {flow_alias!r} after creation'
                raise FlowExecutionNotFoundError(msg)

        _ = await self.admin.a_update_authentication_flow_executions(
            payload={
                **new_execution,
                'requirement': old_execution['requirement'],
                'priority': old_execution['priority'],
            },
            flow_alias=parent_alias,
        )
        _ = await self.admin.a_delete_authentication_flow_execution(old_execution['id'])
        msg = (
            f'execution {old_provider_id!r} replaced with {new_provider_id!r}'
            f' in authentication flow {parent_alias!r}'
        )
        logger.info(msg)

    async def bind_browser_flow(self, flow_alias: str) -> None:
        realm_name = self.settings.keycloak_realm
        realm = await self.admin.a_get_realm(realm_name)
        if realm.get('browserFlow') == flow_alias:
            logger.info(f'browser flow of realm {realm_name!r} already set to {flow_alias!r}')
            return

        _ = await self.admin.a_update_realm(realm_name, {'realm': realm_name, 'browserFlow': flow_alias})
        logger.info(f'browser flow of realm {realm_name!r} set to {flow_alias!r}')

    async def _parent_flow_alias(
        self,
        executions: list[dict[str, Any]],
        execution: dict[str, Any],
        flow_alias: str,
    ) -> str:
        level = execution['level']
        if level == 0:
            return flow_alias

        position = next(i for i, item in enumerate(executions) if item['id'] == execution['id'])
        for item in reversed(executions[:position]):
            if item['level'] == level - 1 and item.get('authenticationFlow'):
                parent_flow = await self.admin.a_get_authentication_flow_for_id(item['flowId'])
                return str(parent_flow['alias'])

        msg = f'parent flow of execution {execution["providerId"]!r} not found in authentication flow {flow_alias!r}'
        raise FlowExecutionNotFoundError(msg)


def _find_execution(executions: list[dict[str, Any]], provider_id: str) -> dict[str, Any] | None:
    for execution in executions:
        if execution.get('providerId') == provider_id:
            return execution
    return None

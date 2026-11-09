from saltbox_keycloak_init.config import Settings
from saltbox_keycloak_init.manage.flow_manager import FlowManager

BUILTIN_BROWSER_FLOW_ALIAS = 'browser'
BUILTIN_LOGIN_FORM_PROVIDER = 'auth-username-password-form'


async def setup_browser_flow(*, flow_mgr: FlowManager, settings: Settings) -> None:
    flow_alias = settings.keycloak_browser_flow_alias
    provider_id = settings.keycloak_login_form_provider

    await flow_mgr.ensure_provider_registered(provider_id)
    await flow_mgr.ensure_flow_copy(source_alias=BUILTIN_BROWSER_FLOW_ALIAS, target_alias=flow_alias)
    await flow_mgr.replace_execution_provider(
        flow_alias=flow_alias,
        old_provider_id=BUILTIN_LOGIN_FORM_PROVIDER,
        new_provider_id=provider_id,
    )
    await flow_mgr.bind_browser_flow(flow_alias)

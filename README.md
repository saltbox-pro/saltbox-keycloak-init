<div align = right>

&ensp;[<kbd> <br> EN <br> </kbd>](./README.md)&ensp;
&ensp;[<kbd> <br> RU <br> </kbd>](./README_RU.md)&ensp;

</div>

---

# Salt.Box Keycloak Init

## Table of Contents

- **[About](#about)**
- **[What it does](#what-it-does)**
- **[Configuration](#configuration)**
  - [Environment variables](#environment-variables)
  - [Secrets](#secrets)
  - [Brute Force Detection](#brute-force-detection)
- **[Browser flow](#browser-flow)**
- **[Project layout](#project-layout)**
- **[Development](#development)**
  - [Environment](#environment)
  - [Verifying your setup](#verifying-your-setup)
  - [Run](#run)
- **[License](#license)**


## About

**Salt.Box Keycloak Init** is a one-shot container that prepares Keycloak for
Salt.Box: it creates the realm, the clients with their roles, the default
users, and the browser authentication flow, then exits.

It runs on every start of [Salt.Box
Compose](https://dev.saltbox.pro/saltbox/saltbox-compose) as the
`keycloak-init` service with `restart: 'no'`. **Every stage is idempotent**:
existing objects are detected and left untouched, so re-running the
container is safe.

## What it does

1. Connects to the `master` realm as the Keycloak `admin` user
2. Creates the `KEYCLOAK_REALM` realm if it does not exist, with the login
   theme, supported locales and [Brute Force
   Detection](#brute-force-detection) settings
3. Configures the [browser flow](#browser-flow) with the Salt.Box login form
4. Creates the Salt.Box Core client and, if its secret is present, the
   Grafana client, from the templates in
   [`client.d/`](./saltbox_keycloak_init/client.d), together with their client
   roles
5. Creates the default user and the administrator, and assigns all client
   roles to the administrator
6. Sets **Direct access grants** of the Salt.Box Core client to
   `KEYCLOAK_CLIENT_DIRECT_ACCESS`
7. Verifies the administrator roles, if `KEYCLOAK_STRICT_ROLE_CHECK` is
   enabled

While Keycloak is starting up, the whole sequence is retried up to 30 times
with a 5 second delay.

## Configuration

Settings are read from environment variables, field names of
[`config.py`](./saltbox_keycloak_init/config.py) in upper case.

### Environment variables

| Variable                        | Default                               | Purpose                                                     |
|---------------------------------|---------------------------------------|-------------------------------------------------------------|
| `KEYCLOAK_URL`                  |                                       | Keycloak base URL, e.g. `http://keycloak:8080/auth/keycloak` |
| `KEYCLOAK_REALM`                |                                       | Salt.Box realm name                                         |
| `KEYCLOAK_CLIENT`               |                                       | Salt.Box Core client ID                                     |
| `KEYCLOAK_CLIENT_GRAFANA`       |                                       | Grafana client ID                                           |
| `KEYCLOAK_USER_NAME`            |                                       | Default user, skipped when empty                            |
| `KEYCLOAK_USER_EMAIL`           |                                       | Default user email                                          |
| `KEYCLOAK_USER_FIRSTNAME`       |                                       | Default user first name                                     |
| `KEYCLOAK_USER_LASTNAME`        |                                       | Default user last name                                      |
| `KEYCLOAK_ADMIN_NAME`           |                                       | Administrator, skipped when empty                           |
| `KEYCLOAK_ADMIN_EMAIL`          |                                       | Administrator email                                         |
| `KEYCLOAK_ADMIN_FIRSTNAME`      |                                       | Administrator first name                                    |
| `KEYCLOAK_ADMIN_LASTNAME`       |                                       | Administrator last name                                     |
| `KEYCLOAK_CLIENT_DIRECT_ACCESS` | `false`                               | Direct access grants of the Salt.Box Core client            |
| `KEYCLOAK_STRICT_ROLE_CHECK`    | `true`                                | Verify administrator roles after setup                      |
| `KEYCLOAK_LOGIN_THEME`          | `saltbox`                             | Login theme of the realm                                    |
| `KEYCLOAK_SUPPORTED_LOCALES`    | `ru, en`                              | Comma separated realm locales                               |
| `KEYCLOAK_DEFAULT_LOCALE`       | `ru`                                  | Default realm locale                                        |
| `KEYCLOAK_BROWSER_FLOW_ALIAS`   | `saltbox browser`                     | Alias of the browser flow copy                              |
| `KEYCLOAK_LOGIN_FORM_PROVIDER`  | `saltbox-auth-username-password-form` | Authenticator provider of the login form                    |
| `KEYCLOAK_INIT_LOG_LEVEL`       | `INFO`                                | Log level                                                   |

### Secrets

Secrets are read from files in `/run/secrets/`:

| Secret                                 | Required                            |
|----------------------------------------|-------------------------------------|
| `keycloak_admin_password`              | Always                              |
| `keycloak_client_saltbox_core_password`| Always                              |
| `keycloak_client_grafana_password`     | No, the Grafana client is skipped without it |
| `saltbox_user_password`                | When `KEYCLOAK_USER_NAME` is set    |
| `saltbox_admin_password`               | When `KEYCLOAK_ADMIN_NAME` is set   |

### Brute Force Detection

The realm is created with Keycloak [Brute Force
Detection](https://www.keycloak.org/docs/latest/server_admin/#password-guess-brute-force-attacks)
in the **Lockout temporarily** mode:

| Variable                              | Default  | Keycloak setting               |
|---------------------------------------|----------|--------------------------------|
| `KEYCLOAK_BF_FAILURE_FACTOR`          | `5`      | `failureFactor`                |
| `KEYCLOAK_BF_MAX_DELTA_TIME_SC`       | `3600`   | `maxDeltaTimeSeconds`          |
| `KEYCLOAK_BF_MAX_FAILURE_WAIT_SC`     | `86400`  | `maxFailureWaitSeconds`        |
| `KEYCLOAK_BF_WAIT_INCREMENT_SC`       | `86400`  | `waitIncrementSeconds`         |
| `KEYCLOAK_BF_MIN_QUICK_LOGIN_WAIT_SC` | `60`     | `minimumQuickLoginWaitSeconds` |
| `KEYCLOAK_BF_QUICK_LOGIN_CHECK_MSC`   | `1000`   | `quickLoginCheckMilliSeconds`  |

With these defaults an account is locked for 24 hours after 5 failed login
attempts within 1 hour. Attempts made less than 1 second apart lock the
account for 1 minute.

> **ATTENTION!** These settings are applied **only when the realm is
> created**. Changing them later has no effect on an existing realm: edit
> them in the Keycloak admin console or recreate the realm

A locked account is unlocked automatically after the lockout period, or by
an administrator: realm `salt.box` → **Users** → the user → **Details** →
switch off **Temporarily locked**.

## Browser flow

The built-in Keycloak login form reveals whether a username exists:
Brute Force Detection locks only existing accounts, so after enough attempts
the response differs for existing and unknown usernames.

To prevent this the login form is replaced with the one from [Salt.Box
Keycloak Authenticator](https://dev.saltbox.pro/saltbox/saltbox-keycloak-authenticator),
which applies the same lockout to unknown usernames. The stage:

1. Checks that the `KEYCLOAK_LOGIN_FORM_PROVIDER` provider is registered in
   Keycloak
2. Copies the built-in `browser` flow to `KEYCLOAK_BROWSER_FLOW_ALIAS`, if
   the copy does not exist yet
3. Replaces the `auth-username-password-form` step of the copy with the
   Salt.Box provider, keeping its position and requirement
4. Binds the copy as the realm browser flow

The built-in `browser` flow is left untouched. To roll back switch the realm
browser flow back to `browser` in **Authentication** of the admin console.

> **ATTENTION!** The Keycloak image must include the Salt.Box Keycloak
> Authenticator provider. Otherwise the stage fails with
> `authenticator provider ... is not registered in keycloak`

## Project layout

- [`main.py`](./saltbox_keycloak_init/main.py) – realm creation and the order
  of stages
- [`config.py`](./saltbox_keycloak_init/config.py) – settings, secrets and
  logging
- [`stages/`](./saltbox_keycloak_init/stages) – setup stages: browser flow,
  clients, users and roles verification
- [`manage/`](./saltbox_keycloak_init/manage) – managers wrapping the Keycloak
  admin API for flows, clients and users
- [`schema/`](./saltbox_keycloak_init/schema) – client, role and user models
  and the lists of client roles
- [`client.d/`](./saltbox_keycloak_init/client.d) – client representation
  templates

## Development

This project uses the following tools:

- [uv](https://docs.astral.sh/uv/) for the environment and dependencies
- [ruff](https://astral.sh/ruff) for Python source linting
- [mypy](https://mypy.readthedocs.io/en/stable/) for static type checking

### Environment

```bash
uv sync --group=dev
source .venv/bin/activate
```

### Verifying your setup

To verify that your setup is working, run the following commands:

```bash
ruff check saltbox_keycloak_init
mypy saltbox_keycloak_init
```

The same checks run in the `lint` stage of the CI pipeline.

### Run

To build the image:

```bash
sudo docker build --target=keycloak-init --tag saltbox-keycloak-init:dev .
```

The `dev` target installs the package in editable mode for local
development.

Use [Salt.Box Compose](https://dev.saltbox.pro/saltbox/saltbox-compose) to run
it together with Keycloak.


## License

Salt.Box Keycloak Init is distributed under the **Apache License 2.0** – see
[`LICENSE.txt`](./LICENSE.txt) for the full text.

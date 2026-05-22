# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [UNRELEASED]

### Added

- Brute Force detection with configurable parameters (`KEYCLOAK_BF_MAX_FAILURE_WAIT_SC`,
  `KEYCLOAK_BF_WAIT_INCREMENT_SC`, `KEYCLOAK_BF_MIN_QUICK_LOGIN_WAIT_SC`,
  `KEYCLOAK_BF_QUICK_LOGIN_CHECK_MSC`, `KEYCLOAK_BF_MAX_DELTA_TIME_SC`,
  `KEYCLOAK_BF_FAILURE_FACTOR` env vars).
- Retry policy for Keycloak initialization attempts.
- CI lint job (mypy, ruff) via GitLab CI pipeline.
- `client.d/` JSON-based configuration for Keycloak clients (Grafana, saltbox-core).

### Changed

- Drop `pydantic`/`pydantic-settings` dependency; replaced with lightweight custom
  `Settings` class reading env vars and Docker secrets directly.
- Rename `GRAFANA_CLIENT` environment variable to `KEYCLOAK_CLIENT_GRAFANA`.
- Refactor code style: single quotes, improved type annotations across all modules.
- `Dockerfile`: simplified by removing multi-stage builder.
- Logging: add datetime format to log formatter.
- `pyproject.toml`: add `package-data` section for `client.d/` JSON files.

### Fixed

- Docker secret extraction in `config.py`.
- Initialization of Salt.Box entities incorrectly applied to master realm instead of
  target realm.
- `SecretsUsedInArgOrEnv` linting error in `Dockerfile`.
- mypy type errors.

### Removed

- `DEFAULT_QUICK_LOGIN_CHECK_TIME` variable.
- Builder stage from `Dockerfile`.
- `--prefix` flag from pip install in `Dockerfile`.
- `pydantic` and `pydantic-settings` from dependencies.

<div align = right>

&ensp;[<kbd> <br> EN <br> </kbd>](./README.md)&ensp;
&ensp;[<kbd> <br> RU <br> </kbd>](./README_RU.md)&ensp;

</div>

---

# Salt.Box Keycloak Init

## Содержание

- **[Описание](#описание)**
- **[Что делает контейнер](#что-делает-контейнер)**
- **[Настройка](#настройка)**
  - [Переменные окружения](#переменные-окружения)
  - [Секреты](#секреты)
  - [Brute Force Detection](#brute-force-detection)
- **[Browser flow](#browser-flow)**
- **[Структура проекта](#структура-проекта)**
- **[Разработка](#разработка)**
  - [Окружение](#окружение)
  - [Проверка окружения](#проверка-окружения)
  - [Запуск](#запуск)
- **[Лицензия](#лицензия)**


## Описание

**Salt.Box Keycloak Init** – одноразовый контейнер, который готовит Keycloak
для Salt.Box: создаёт realm, клиентов с их ролями, пользователей по
умолчанию и browser flow аутентификации, после чего завершается.

Он запускается при каждом старте [Salt.Box
Compose](https://dev.saltbox.pro/saltbox/saltbox-compose) как сервис
`keycloak-init` с `restart: 'no'`. **Каждый этап идемпотентен**: уже
существующие объекты определяются и не изменяются, поэтому повторный запуск
контейнера безопасен.

## Что делает контейнер

1. Подключается к realm `master` под пользователем Keycloak `admin`
2. Создаёт realm `KEYCLOAK_REALM`, если его нет, с темой входа,
   поддерживаемыми локалями и настройками [Brute Force
   Detection](#brute-force-detection)
3. Настраивает [browser flow](#browser-flow) с формой входа Salt.Box
4. Создаёт клиента Salt.Box Core и, если есть его секрет, клиента Grafana по
   шаблонам из [`client.d/`](./saltbox_keycloak_init/client.d) вместе с их
   клиентскими ролями
5. Создаёт пользователя по умолчанию и администратора, назначает
   администратору все клиентские роли
6. Выставляет **Direct access grants** клиента Salt.Box Core в значение
   `KEYCLOAK_CLIENT_DIRECT_ACCESS`
7. Проверяет роли администратора, если включён `KEYCLOAK_STRICT_ROLE_CHECK`

Пока Keycloak запускается, вся последовательность повторяется до 30 раз с
задержкой 5 секунд.

## Настройка

Настройки читаются из переменных окружения, это имена полей
[`config.py`](./saltbox_keycloak_init/config.py) в верхнем регистре.

### Переменные окружения

| Переменная                      | По умолчанию                          | Назначение                                                  |
|---------------------------------|---------------------------------------|-------------------------------------------------------------|
| `KEYCLOAK_URL`                  |                                       | Базовый URL Keycloak, например `http://keycloak:8080/auth/keycloak` |
| `KEYCLOAK_REALM`                |                                       | Имя realm Salt.Box                                          |
| `KEYCLOAK_CLIENT`               |                                       | ID клиента Salt.Box Core                                    |
| `KEYCLOAK_CLIENT_GRAFANA`       |                                       | ID клиента Grafana                                          |
| `KEYCLOAK_USER_NAME`            |                                       | Пользователь по умолчанию, пропускается, если пусто         |
| `KEYCLOAK_USER_EMAIL`           |                                       | Email пользователя по умолчанию                             |
| `KEYCLOAK_USER_FIRSTNAME`       |                                       | Имя пользователя по умолчанию                               |
| `KEYCLOAK_USER_LASTNAME`        |                                       | Фамилия пользователя по умолчанию                           |
| `KEYCLOAK_ADMIN_NAME`           |                                       | Администратор, пропускается, если пусто                     |
| `KEYCLOAK_ADMIN_EMAIL`          |                                       | Email администратора                                        |
| `KEYCLOAK_ADMIN_FIRSTNAME`      |                                       | Имя администратора                                          |
| `KEYCLOAK_ADMIN_LASTNAME`       |                                       | Фамилия администратора                                      |
| `KEYCLOAK_CLIENT_DIRECT_ACCESS` | `false`                               | Direct access grants клиента Salt.Box Core                  |
| `KEYCLOAK_STRICT_ROLE_CHECK`    | `true`                                | Проверять роли администратора после настройки               |
| `KEYCLOAK_LOGIN_THEME`          | `saltbox`                             | Тема входа realm                                            |
| `KEYCLOAK_SUPPORTED_LOCALES`    | `ru, en`                              | Локали realm через запятую                                  |
| `KEYCLOAK_DEFAULT_LOCALE`       | `ru`                                  | Локаль realm по умолчанию                                   |
| `KEYCLOAK_BROWSER_FLOW_ALIAS`   | `saltbox browser`                     | Алиас копии browser flow                                    |
| `KEYCLOAK_LOGIN_FORM_PROVIDER`  | `saltbox-auth-username-password-form` | Провайдер аутентификации для формы входа                    |
| `KEYCLOAK_INIT_LOG_LEVEL`       | `INFO`                                | Уровень логирования                                         |

### Секреты

Секреты читаются из файлов в `/run/secrets/`:

| Секрет                                 | Обязателен                          |
|----------------------------------------|-------------------------------------|
| `keycloak_admin_password`              | Всегда                              |
| `keycloak_client_saltbox_core_password`| Всегда                              |
| `keycloak_client_grafana_password`     | Нет, без него клиент Grafana не создаётся |
| `saltbox_user_password`                | Если задан `KEYCLOAK_USER_NAME`     |
| `saltbox_admin_password`               | Если задан `KEYCLOAK_ADMIN_NAME`    |

### Brute Force Detection

Realm создаётся с механизмом Keycloak [Brute Force
Detection](https://www.keycloak.org/docs/latest/server_admin/#password-guess-brute-force-attacks)
в режиме **Lockout temporarily**:

| Переменная                            | По умолчанию | Настройка Keycloak             |
|---------------------------------------|--------------|--------------------------------|
| `KEYCLOAK_BF_FAILURE_FACTOR`          | `5`          | `failureFactor`                |
| `KEYCLOAK_BF_MAX_DELTA_TIME_SC`       | `3600`       | `maxDeltaTimeSeconds`          |
| `KEYCLOAK_BF_MAX_FAILURE_WAIT_SC`     | `86400`      | `maxFailureWaitSeconds`        |
| `KEYCLOAK_BF_WAIT_INCREMENT_SC`       | `86400`      | `waitIncrementSeconds`         |
| `KEYCLOAK_BF_MIN_QUICK_LOGIN_WAIT_SC` | `60`         | `minimumQuickLoginWaitSeconds` |
| `KEYCLOAK_BF_QUICK_LOGIN_CHECK_MSC`   | `1000`       | `quickLoginCheckMilliSeconds`  |

С этими значениями учётная запись блокируется на 24 часа после 5 неудачных
попыток входа в течение 1 часа. Попытки чаще раза в секунду блокируют
учётную запись на 1 минуту.

> **ВНИМАНИЕ!** Эти настройки применяются **только при создании realm**.
> Их изменение позже не влияет на существующий realm: измените их в
> консоли администратора Keycloak или пересоздайте realm

Заблокированная учётная запись разблокируется автоматически по истечении
срока блокировки или администратором: realm `salt.box` → **Users** →
пользователь → **Details** → выключить **Temporarily locked**.

## Browser flow

Стандартная форма входа Keycloak позволяет определить, существует ли
логин: Brute Force Detection блокирует только существующие учётные записи,
поэтому после нескольких попыток ответ для существующего и несуществующего
логина различается.

Чтобы этого избежать, форма входа заменяется формой из [Salt.Box Keycloak
Authenticator](https://dev.saltbox.pro/saltbox/saltbox-keycloak-authenticator),
которая применяет такую же блокировку к несуществующим логинам. Этап:

1. Проверяет, что провайдер `KEYCLOAK_LOGIN_FORM_PROVIDER` зарегистрирован в
   Keycloak
2. Копирует встроенный flow `browser` в `KEYCLOAK_BROWSER_FLOW_ALIAS`, если
   копии ещё нет
3. Заменяет в копии шаг `auth-username-password-form` на провайдер
   Salt.Box, сохраняя его позицию и требование
4. Назначает копию browser flow realm

Встроенный flow `browser` не изменяется. Чтобы откатиться, верните
`browser` как browser flow realm в разделе **Authentication** консоли
администратора.

> **ВНИМАНИЕ!** Образ Keycloak должен содержать провайдер Salt.Box Keycloak
> Authenticator. Иначе этап завершится ошибкой
> `authenticator provider ... is not registered in keycloak`

## Структура проекта

- [`main.py`](./saltbox_keycloak_init/main.py) – создание realm и порядок
  этапов
- [`config.py`](./saltbox_keycloak_init/config.py) – настройки, секреты и
  логирование
- [`stages/`](./saltbox_keycloak_init/stages) – этапы настройки: browser
  flow, клиенты, пользователи и проверка ролей
- [`manage/`](./saltbox_keycloak_init/manage) – менеджеры над admin API
  Keycloak для flow, клиентов и пользователей
- [`schema/`](./saltbox_keycloak_init/schema) – модели клиентов, ролей и
  пользователей и списки клиентских ролей
- [`client.d/`](./saltbox_keycloak_init/client.d) – шаблоны представлений
  клиентов

## Разработка

В проекте используются следующие инструменты:

- [uv](https://docs.astral.sh/uv/) для окружения и зависимостей
- [ruff](https://astral.sh/ruff) для линтинга Python-кода
- [mypy](https://mypy.readthedocs.io/en/stable/) для статической проверки
  типов

### Окружение

```bash
uv sync --group=dev
source .venv/bin/activate
```

### Проверка окружения

Чтобы проверить, что окружение настроено, выполните:

```bash
ruff check saltbox_keycloak_init
mypy saltbox_keycloak_init
```

Те же проверки запускаются на стадии `lint` CI-пайплайна.

### Запуск

Сборка образа:

```bash
sudo docker build --target=keycloak-init --tag saltbox-keycloak-init:dev .
```

Цель `dev` устанавливает пакет в редактируемом режиме для локальной
разработки.

Для запуска вместе с Keycloak используйте [Salt.Box
Compose](https://dev.saltbox.pro/saltbox/saltbox-compose).


## Лицензия

Salt.Box Keycloak Init распространяется под лицензией **Apache License 2.0** –
полный текст в [`LICENSE.txt`](./LICENSE.txt).

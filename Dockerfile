ARG BASE_IMG="registry.altlinux.org/alt/alt:p11"

FROM "$BASE_IMG" AS keycloak-init
LABEL version="1.2"
LABEL release="0"

RUN \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
<<EOF
set -e
mkdir --parents /var/cache/apt/archives/partial/ /var/lib/apt/lists/partial/
apt-get update
apt-get install -y java-21-openjdk wget python3-module-pip glibc-pthread
EOF

WORKDIR /build
COPY pyproject.toml LICENSE.txt README.md ./
COPY saltbox_keycloak_init/ saltbox_keycloak_init/
RUN python3 -m pip install --no-cache-dir .
WORKDIR /

ENV KEYCLOAK_URL=''
ENV KEYCLOAK_REALM=''
ENV KEYCLOAK_CLIENT=''
ENV KEYCLOAK_ADMIN_PASSWORD=''
ENV KEYCLOAK_CLIENT_PASSWORD=''

ENV KEYCLOAK_USER_NAME=''
ENV KEYCLOAK_USER_EMAIL=''
ENV KEYCLOAK_USER_FIRSTNAME=''
ENV KEYCLOAK_USER_LASTNAME=''

ENV KEYCLOAK_ADMIN_NAME=''
ENV KEYCLOAK_ADMIN_EMAIL=''
ENV KEYCLOAK_ADMIN_FIRSTNAME=''
ENV KEYCLOAK_ADMIN_LASTNAME=''

ENV KEYCLOAK_CLIENT_DIRECT_ACCESS='false'
ENV KEYCLOAK_STRICT_ROLE_CHECK='true'
ENV LOG_LEVEL='INFO'

ENTRYPOINT ["saltbox-keycloak-init"]


FROM "$BASE_IMG" AS dev

RUN \
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
<<EOF
set -e
mkdir --parents /var/cache/apt/archives/partial/ /var/lib/apt/lists/partial/
apt-get update
apt-get install -y java-21-openjdk wget python3-module-pip glibc-pthread
EOF

WORKDIR /app
COPY pyproject.toml LICENSE.txt README.md ./
COPY saltbox_keycloak_init/ saltbox_keycloak_init/

RUN python3 -m pip install --no-cache-dir -e .

ENTRYPOINT ["saltbox-keycloak-init"]

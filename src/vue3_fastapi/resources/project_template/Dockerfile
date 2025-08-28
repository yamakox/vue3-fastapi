ARG PYTHON_VERSION={{:Pythonバージョン:}}
ARG ALPINE_VERSION=3.21

FROM ghcr.io/astral-sh/uv:alpine

# ホストのファイルをコンテナにコピー(.gitも含む)
WORKDIR "/opt/app"
COPY ./ ./

WORKDIR "/opt/app/frontend"
RUN \
    apk update && \
    apk add --no-cache git npm && \
    npm install && \
    npm run build -- --mode backend

WORKDIR "/opt/app/backend"
RUN \
    ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime && \
    apk update && \
    apk add --no-cache \
        git linux-headers build-base autoconf g++ gcc libc-dev make && \
    uv build --wheel

FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION}

ARG HOST=0.0.0.0
ARG PORT=8000

ENV HOST=$HOST
ENV PORT=$PORT

WORKDIR "/opt/app"
COPY --from=0 /opt/app/backend/dist/*.whl ./
RUN \
    apk update && \
    apk add --no-cache --virtual .build-deps \
        git linux-headers build-base autoconf g++ gcc libc-dev make && \
    python3 -m pip install --root-user-action ignore -U pip setuptools *.whl && \
    apk del .build-deps

# https://docs.docker.com/reference/build-checks/json-args-recommended/
SHELL ["/bin/sh", "-c"]
CMD python3 -m uvicorn --host=$HOST --port=$PORT --factory {{:Pythonパッケージ名:}}:create_app --reload

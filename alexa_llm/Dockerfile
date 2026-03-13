ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache python3 py3-pip py3-virtualenv bash

WORKDIR /app

COPY run.sh /run.sh

RUN chmod a+x /run.sh \
    && python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir fastapi uvicorn

CMD [ "/run.sh" ]
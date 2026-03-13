ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip

WORKDIR /app
COPY run.sh /run.sh
RUN chmod a+x /run.sh

RUN pip3 install --no-cache-dir fastapi uvicorn

CMD [ "/run.sh" ]
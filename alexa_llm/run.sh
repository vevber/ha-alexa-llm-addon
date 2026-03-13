#!/usr/bin/with-contenv bashio

echo "Python im venv:"
ls -l /opt/venv/bin/python
echo "Uvicorn im venv:"
ls -l /opt/venv/bin/uvicorn || true

cat <<'PY' > /app/server.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "running"}
PY

exec /opt/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8000 --app-dir /app
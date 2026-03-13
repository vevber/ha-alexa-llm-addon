#!/usr/bin/with-contenv bashio

cat <<'PY' > /app/server.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "running"}
PY

python3 -m uvicorn server:app --host 0.0.0.0 --port 8000 --app-dir /app
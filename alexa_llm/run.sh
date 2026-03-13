#!/usr/bin/with-contenv bashio

echo "Python im venv:"
ls -l /opt/venv/bin/python
echo "Uvicorn im venv:"
ls -l /opt/venv/bin/uvicorn || true

cat <<'PY' > /app/server.py
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/alexa")
async def alexa(request: Request):
    data = await request.json()

    request_type = data.get("request", {}).get("type")

    if request_type == "LaunchRequest":
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Hallo. Ich bin bereit."
                },
                "shouldEndSession": False
            }
        }

    if request_type == "IntentRequest":
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Die Verbindung zu deinem Home Assistant Server funktioniert."
                },
                "shouldEndSession": True
            }
        }

    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Unbekannte Anfrage."
            },
            "shouldEndSession": True
        }
    }
PY

exec /opt/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8000 --app-dir /app
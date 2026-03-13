#!/usr/bin/with-contenv bashio

echo "Python im venv:"
ls -l /opt/venv/bin/python
echo "Uvicorn im venv:"
ls -l /opt/venv/bin/uvicorn || true

cat <<'PY' > /app/server.py
from fastapi import FastAPI, Request

app = FastAPI()

def alexa_response(text: str, end_session: bool = True):
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": text
            },
            "shouldEndSession": end_session
        }
    }

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/alexa")
async def alexa(request: Request):
    data = await request.json()

    request_type = data.get("request", {}).get("type")

    if request_type == "LaunchRequest":
        return alexa_response("Hallo. Stell mir einfach eine Frage.", False)

    if request_type == "IntentRequest":
        intent = data.get("request", {}).get("intent", {})
        intent_name = intent.get("name", "")
        slots = intent.get("slots", {})

        question = ""
        if "question" in slots:
            question = slots["question"].get("value", "")

        if intent_name == "AskAnythingIntent":
            if not question:
                return alexa_response("Ich habe keine Frage erkannt.")

            q = question.lower().strip()

            if "quersumme" in q:
                return alexa_response(
                    "Die Quersumme ist die Summe aller Ziffern einer Zahl. "
                    "Bei 123 ist die Quersumme zum Beispiel 1 plus 2 plus 3, also 6."
                )

            if "hallo" in q:
                return alexa_response("Hallo.")

            return alexa_response(f"Du hast gefragt: {question}")

        if intent_name == "AMAZON.HelpIntent":
            return alexa_response(
                "Du kannst mich zum Beispiel fragen: Was ist eine Quersumme?"
            )

        if intent_name in ["AMAZON.StopIntent", "AMAZON.CancelIntent"]:
            return alexa_response("Okay.")

    return alexa_response("Das habe ich nicht verstanden.")
PY

exec /opt/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8000 --app-dir /app
import os

from fastapi import FastAPI, Request
from openai import OpenAI

app = FastAPI()

SYSTEM_PROMPT = (
    "You answer for Alexa in German. "
    "Keep answers short, clear and natural for speech. "
    "Maximum 3 short sentences. "
    "Do not use markdown, lists or special formatting."
)


def alexa_response(text: str, should_end_session: bool = True) -> dict:
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": text},
            "shouldEndSession": should_end_session,
        },
    }


def get_slot_value(intent: dict, *slot_names: str) -> str:
    slots = intent.get("slots", {})
    for slot_name in slot_names:
        slot = slots.get(slot_name, {})
        value = slot.get("value", "").strip()
        if value:
            return value
    return ""


def ask_llm(question: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return (
            "Der OpenAI API Key fehlt noch im Add-on. "
            "Bitte trage ihn in den Add-on Optionen ein."
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "180"))
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
    )

    answer = completion.choices[0].message.content or ""
    return " ".join(answer.split())[:450] or "Dazu habe ich gerade keine Antwort."


@app.get("/")
def root() -> dict:
    return {"status": "running"}


@app.post("/alexa")
async def alexa(request: Request) -> dict:
    data = await request.json()
    request_type = data.get("request", {}).get("type")

    if request_type == "LaunchRequest":
        return alexa_response("Hallo. Stell mir einfach eine Frage.", should_end_session=False)

    if request_type != "IntentRequest":
        return alexa_response("Unbekannte Anfrage.")

    intent = data.get("request", {}).get("intent", {})
    intent_name = intent.get("name", "")

    if intent_name == "AskAnythingIntent":
        question = get_slot_value(intent, "question", "query")
        if not question:
            return alexa_response("Ich habe keine Frage erkannt. Bitte versuch es noch einmal.")
        try:
            return alexa_response(ask_llm(question))
        except Exception:
            return alexa_response(
                "Die Anfrage an das Sprachmodell hat gerade nicht funktioniert. Bitte versuch es gleich noch einmal."
            )

    if intent_name in ["AMAZON.FallbackIntent"]:
        return alexa_response("Bitte stelle eine konkrete Frage, zum Beispiel: Was ist eine Quersumme?")

    if intent_name in ["AMAZON.HelpIntent"]:
        return alexa_response("Du kannst mich zum Beispiel fragen: Was ist eine Quersumme?")

    if intent_name in ["AMAZON.StopIntent", "AMAZON.CancelIntent"]:
        return alexa_response("Okay.")

    return alexa_response("Das habe ich nicht verstanden.")
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


def alexa_response(text: str, should_end_session: bool = True, reprompt: str = "") -> dict:
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": text},
            "shouldEndSession": should_end_session,
        },
    }
    if reprompt and not should_end_session:
        response["response"]["reprompt"] = {
            "outputSpeech": {"type": "PlainText", "text": reprompt}
        }
    return response


def get_slot_value(intent: dict, *slot_names: str) -> str:
    slots = intent.get("slots", {})
    for slot_name in slot_names:
        slot = slots.get(slot_name, {})
        value = slot.get("value", "").strip()
        if value:
            return value

    # Fallback: use the first non-empty slot value in case slot names differ.
    for slot in slots.values():
        value = str(slot.get("value", "")).strip()
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


def normalize_question(question: str) -> str:
    q = question.lower().strip()
    # Alexa transcripts may contain spaced abbreviations like "k. i.".
    q = q.replace("k. i.", "ki").replace("k i", "ki")
    return q


@app.get("/")
def root() -> dict:
    return {"status": "running"}


@app.post("/alexa")
async def alexa(request: Request) -> dict:
    data = await request.json()
    request_type = data.get("request", {}).get("type")

    if request_type == "LaunchRequest":
        return alexa_response(
            "Hallo. Stell mir einfach eine Frage.",
            should_end_session=False,
            reprompt="Zum Beispiel: Was ist eine Quersumme?",
        )

    if request_type != "IntentRequest":
        return alexa_response("Unbekannte Anfrage.")

    intent = data.get("request", {}).get("intent", {})
    intent_name = intent.get("name", "")

    if intent_name == "AskAnythingIntent":
        question = get_slot_value(intent, "question", "query")
        if not question:
            return alexa_response(
                "Ich habe keine Frage erkannt. Frag bitte noch einmal, zum Beispiel: Was ist eine Quersumme?",
                should_end_session=False,
                reprompt="Frag mich zum Beispiel: Was ist eine Quersumme?",
            )

        normalized = normalize_question(question)
        active_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        if "mit was fuer einer ki rede ich" in normalized or "mit welcher ki rede ich" in normalized:
            return alexa_response(
                f"Du redest gerade mit dem Modell {active_model} ueber dein OpenAI-Konto.",
                should_end_session=False,
                reprompt="Stell mir gern noch eine Frage.",
            )

        if "welche ki modelle" in normalized or "ki modelle gibt es" in normalized:
            return alexa_response(
                "Es gibt zum Beispiel GPT 4o mini und GPT 4.1 von OpenAI, Claude Modelle von Anthropic, "
                "Gemini von Google und Llama Modelle von Meta.",
                should_end_session=False,
                reprompt="Wenn du willst, erklaere ich dir die Unterschiede.",
            )

        try:
            return alexa_response(
                ask_llm(question),
                should_end_session=False,
                reprompt="Stell mir gern noch eine Frage.",
            )
        except Exception as exc:
            message = str(exc).lower()
            if "insufficient_quota" in message or "exceeded your current quota" in message:
                return alexa_response(
                    "Das OpenAI-Konto hat aktuell kein Guthaben. Bitte pruefe Billing und probiere es erneut.",
                    should_end_session=False,
                    reprompt="Sobald es wieder geht, stelle deine Frage erneut.",
                )
            return alexa_response(
                "Die Anfrage an das Sprachmodell hat gerade nicht funktioniert. Bitte versuch es gleich noch einmal.",
                should_end_session=False,
                reprompt="Du kannst die Frage sofort wiederholen.",
            )

    if intent_name in ["AMAZON.FallbackIntent"]:
        return alexa_response(
            "Bitte stelle eine konkrete Frage, zum Beispiel: Was ist eine Quersumme?",
            should_end_session=False,
            reprompt="Stell eine Frage wie: Was ist eine Quersumme?",
        )

    if intent_name in ["AMAZON.HelpIntent"]:
        return alexa_response(
            "Du kannst mich zum Beispiel fragen: Was ist eine Quersumme?",
            should_end_session=False,
            reprompt="Frag zum Beispiel: Was ist eine Quersumme?",
        )

    if intent_name in ["AMAZON.StopIntent", "AMAZON.CancelIntent"]:
        return alexa_response("Okay.")

    return alexa_response("Das habe ich nicht verstanden.")
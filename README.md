# Alexa LLM Home Assistant Add-on

Dieses Repository enthaelt ein Home Assistant Add-on, das Alexa-Anfragen (`/alexa`) entgegennimmt und ueber ein OpenAI-Modell beantwortet.

## Status

- Add-on `alexa_llm` ist fuer `aarch64` und `amd64` ausgelegt.
- HTTP-Endpunkte:
  - `GET /` -> Healthcheck
  - `POST /alexa` -> Alexa Request Handler
- Release-Stand: `v1.1.0`

## Ordnerstruktur

```text
.
|- repository.json
|- README.md
`- alexa_llm/
   |- config.yaml
   |- Dockerfile
   |- run.sh
   `- server.py
```

## Add-on Optionen

In Home Assistant im Add-on unter `Configuration`:

- `openai_api_key` (pflichtig)
- `openai_model` (Default: `gpt-4o-mini`)
- `openai_max_tokens` (Default: `180`, Bereich `32..512`)
- `openai_temperature` (Default: `0.3`, Bereich `0..1`)

Beispiel:

```yaml
openai_api_key: "sk-..."
openai_model: "gpt-4o-mini"
openai_max_tokens: 180
openai_temperature: 0.3
```

## Installation in Home Assistant

1. Repo in Home Assistant Add-on Store als Repository hinzufuegen.
2. Add-on `Alexa LLM Server` installieren.
3. Optionen setzen (mindestens `openai_api_key`).
4. Add-on starten.
5. Testen:
   - `http://<HA_IP>:8000/` -> `{"status":"running"}`

## Lokaler Endpoint-Test (PowerShell)

```powershell
Invoke-RestMethod `
  -Uri "http://<HA_IP>:8000/alexa" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{
    "request": {
      "type": "IntentRequest",
      "intent": {
        "name": "AskAnythingIntent",
        "slots": {
          "question": { "name": "question", "value": "Was ist eine Quersumme?" }
        }
      }
    }
  }' | ConvertTo-Json -Depth 10
```

## Alexa Skill Minimal-Konfiguration

Intent: `AskAnythingIntent`

Slot:

- `question` vom Typ `AMAZON.SearchQuery`

Beispiel-Utterances:

- `was ist {question}`
- `erklaere mir {question}`
- `was bedeutet {question}`

## Wichtiger Hinweis fuer Alexa Endpoint

Alexa akzeptiert fuer produktive Endpoints nur oeffentlich erreichbares HTTPS.

Der lokale Test ueber `http://<HA_IP>:8000` ist nur fuer interne Verifikation.

## Sicherheit

- API-Keys niemals im Repo speichern.
- GitHub Token nur im Credential Manager/Secret Store hinterlegen.
- Bei versehentlich geteilten Tokens sofort widerrufen und neu erstellen.

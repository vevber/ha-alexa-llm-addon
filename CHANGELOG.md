# Changelog

Alle relevanten Änderungen an diesem Projekt werden hier dokumentiert.

---

## [1.1.0] - 2026-03-13

### Neu
- `server.py` mit echtem OpenAI-LLM-Backend (statt statischer Testantworten)
- Add-on-Optionen in `config.yaml`: `openai_api_key`, `openai_model`, `openai_max_tokens`, `openai_temperature`
- `run.sh` liest Optionen sicher via `bashio::config` und exportiert sie als Umgebungsvariablen
- `Dockerfile` kopiert `server.py` als separate Datei ins Image und installiert `openai`
- `README.md` mit Schnellstart, Optionsbeschreibung, PowerShell-Testbefehl und Alexa-Skill-Konfiguration
- `.gitignore` schließt lokale `_backup/`-Artefakte aus

### Geändert
- `run.sh` generiert `server.py` nicht mehr inline per `cat <<'PY'`
- Alexa-Intent-Handling robuster: Slot-Fallback auf `query`, Fehlerbehandlung bei API-Fehlern

### Sicherheit
- API-Key wird über Add-on-Options als `password`-Schema verwaltet (nicht im Klartext in Konfigurationsdateien)

---

## [1.0.5] - 2026-03-13 (Basis vor LLM-Umstellung)

### Stand
- Testserver mit statischen Alexa-Antworten
- `AskAnythingIntent` mit hardcodierten Keyword-Checks (z. B. „quersumme")
- `run.sh` generierte `server.py` inline
- Kein `openai`-Paket im Image

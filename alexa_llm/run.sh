#!/usr/bin/with-contenv bashio

export OPENAI_API_KEY="$(bashio::config 'openai_api_key')"
export OPENAI_MODEL="$(bashio::config 'openai_model')"
export OPENAI_MAX_TOKENS="$(bashio::config 'openai_max_tokens')"
export OPENAI_TEMPERATURE="$(bashio::config 'openai_temperature')"

bashio::log.info "Starting Alexa LLM server on :8000"
bashio::log.info "Configured model: ${OPENAI_MODEL}"

exec /opt/venv/bin/python -m uvicorn server:app --host 0.0.0.0 --port 8000 --app-dir /app
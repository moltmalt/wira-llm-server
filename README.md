# wira-llm-server

Hybrid LLM server for the WIRA disaster intelligence assistant.

## Quick start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in real keys
python app.py           # → http://localhost:5000
```

## Endpoints

| Route | Method | Description |
|---|---|---|
| `/api/chat` | POST | Chat with the assistant |
| `/health` | GET | Provider health check |

### POST `/api/chat`

```json
{
  "question": "What should I do during a flood?",
  "context": {
    "hazardType": "FLOOD",
    "location": "Kuching, Sarawak"
  }
}
```

Response:
```json
{
  "answer": "...",
  "provider": "sea-lion",
  "disclaimer": "..."
}
```

## Architecture

```
Request → LLMRouter
  ├─ SEA-LION available? → try SEA-LION
  │   └─ failure? → try Gemini
  └─ SEA-LION at limit → try Gemini
      └─ failure? → 503
```

SEA-LION is primary (via HF Inference, 10 RPM cap). Gemini is overflow/fallback.

## Tests

```bash
python -m pytest tests/ -v
```

"""
WIRA LLM Server — Flask application.
Exposes ``/api/chat`` (POST) and ``/health`` (GET).
"""

import logging

from flask import Flask, jsonify, request

from config import Config
from providers import SeaLionProvider, GeminiProvider
from services import LLMRouter, build_prompt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

DISCLAIMER = (
    "This assistant provides general preparedness guidance only and "
    "cannot issue warnings or operational commands."
)


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)

    # ------------------------------------------------------------------
    # Initialise providers + router
    # ------------------------------------------------------------------
    sea_lion = SeaLionProvider(
        api_token=Config.HF_API_TOKEN,
        model_id=Config.HF_MODEL_ID,
        rpm_limit=Config.HF_RPM_LIMIT,
        timeout=Config.LLM_TIMEOUT_SECONDS,
    )
    gemini = GeminiProvider(
        api_key=Config.GEMINI_API_KEY,
        model=Config.GEMINI_MODEL,
        timeout=Config.LLM_TIMEOUT_SECONDS,
    )
    router = LLMRouter(primary=sea_lion, fallback=gemini)

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------

    @app.post("/api/chat")
    def chat():
        body = request.get_json(silent=True) or {}
        question = (body.get("question") or "").strip()

        if not question:
            return jsonify({"error": "question is required"}), 400
        if len(question) > 500:
            return jsonify({"error": "question must be ≤ 500 characters"}), 400

        context = body.get("context") or {}
        prompt = build_prompt(
            question=question,
            hazard_type=context.get("hazardType"),
            location=context.get("location"),
        )

        try:
            answer, provider_name = router.generate(prompt)
        except RuntimeError:
            return jsonify({
                "answer": (
                    "All language model providers are currently unavailable. "
                    "Please try again shortly."
                ),
                "provider": "none",
                "disclaimer": DISCLAIMER,
            }), 503

        return jsonify({
            "answer": answer,
            "provider": provider_name,
            "disclaimer": DISCLAIMER,
        })

    @app.get("/health")
    def health():
        return jsonify({
            "status": "ok",
            "providers": {
                "sea_lion": sea_lion.is_available(),
                "gemini": gemini.is_available(),
            },
        })

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=Config.FLASK_PORT, debug=True)

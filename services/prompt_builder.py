"""Disaster-context prompt shaping.

Injects hazard type, location, and system role into the raw user
question so the LLM responds with relevant preparedness information.
"""

SYSTEM_PREFIX = (
    "You are WIRA, a disaster preparedness and response assistant for "
    "communities in Borneo and Southeast Asia. Provide concise, actionable "
    "safety guidance. Always remind users to follow official local "
    "authority instructions. Do not issue warnings or operational commands."
)


def build_prompt(
    question: str,
    hazard_type: str | None = None,
    location: str | None = None,
) -> str:
    """Build a contextualised prompt string for the LLM."""
    parts: list[str] = [f"System: {SYSTEM_PREFIX}"]

    context_lines: list[str] = []
    if hazard_type:
        context_lines.append(f"Hazard type: {hazard_type}")
    if location:
        context_lines.append(f"Location: {location}")
    if context_lines:
        parts.append(f"Context: {', '.join(context_lines)}")

    parts.append(f"User: {question}")
    return "\n\n".join(parts)

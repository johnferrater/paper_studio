import os

from openai import OpenAI

SYSTEM_PROMPT = (
    "You are Paper Studio's research writing assistant for students and teachers. "
    "Help refine research questions, outline chapters, and improve academic writing. "
    "Always remind the user that AI suggestions are not verified sources and must be "
    "checked. Keep answers concise and practical."
)


def build_instructions(project):
    parts = [SYSTEM_PROMPT, f"Project title: {project.title}."]
    if project.abstract:
        parts.append(f"Project abstract: {project.abstract}")
    return " ".join(parts)


def ask_assistant(project, history, prompt):
    """Return the assistant reply. Degrades gracefully without an API key."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return (
            "The AI assistant is not configured yet. Ask an administrator to add "
            "OPENAI_API_KEY to the .env file."
        )

    messages = [{"role": item.role, "content": item.content} for item in history]
    messages.append({"role": "user", "content": prompt})

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            instructions=build_instructions(project),
            input=messages,
        )
        return (response.output_text or "").strip() or "No response was returned."
    except Exception as exc:  # noqa: BLE001 - surface a friendly message to the UI
        return f"The AI assistant is unavailable right now ({exc.__class__.__name__})."

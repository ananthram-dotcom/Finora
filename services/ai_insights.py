from config.settings import settings
from core.logger import get_logger

logger = get_logger(__name__)

try:
    import google.generativeai as genai
except Exception:
    genai = None


def generate_insight(summary_text: str) -> str:
    if not settings.ENABLE_AI or genai is None:
        return "AI insights are disabled."

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-pro")

        prompt = f"""
Analyze the following financial summary and provide concise insights
and recommendations in bullet points.

SUMMARY:
{summary_text}
"""

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception:
        logger.exception("AI insight generation failed.")
        return "Unable to generate AI insights."

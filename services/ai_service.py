import google.generativeai as genai
from config.settings import GEMINI_API_KEY, ENABLE_AI
from core.logger import logger
from datetime import datetime

if ENABLE_AI:
    genai.configure(api_key=GEMINI_API_KEY)

CATEGORY_LIST = """
Strictly use only these categories and subcategories:
- Food: Groceries, Dining Out, Snacks & Beverages
- Housing: Rent, Electricity, Utilities & Maintenance
- Transportation: Fuel & Travel, Public Transport
- Health: Medicine & Consultation, Insurance
- Entertainment: Movies & Streaming, Events
- Personal: Shopping, Gifts & Donations
- Utilities: Mobile & Internet
- Income: Salary / Wages, Freelance / Projects, Other Income
- General: Anything else (only if nothing fits)
"""

def parse_with_ai(message: str):
    if not ENABLE_AI:
        return None

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
You are an accurate transaction classifier.

From this user message extract:
- type: "Income" or "Expense"
- amount: number (float)
- category: must be one from the list
- subcategory: must be one from the list
- description: short clean summary

Use ONLY these categories/subcategories:
{CATEGORY_LIST}

Message: "{message}"

Return **ONLY** valid JSON, nothing else:
{{
  "type": "Income" or "Expense",
  "amount": 1234.56,
  "category": "Food",
  "subcategory": "Groceries",
  "description": "Bought vegetables"
}}

If uncertain → use "General" / "General".
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:].split("```")[0].strip()
        data = eval(text)

        data["date"] = datetime.now().strftime("%Y-%m-%d")
        return data

    except Exception as e:
        logger.error(f"Gemini parsing failed: {e}")
        return None


def generate_insights(summary_text: str):
    if not ENABLE_AI:
        return None

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
You are a helpful family finance advisor.

Based on this house data:
{summary_text}

Give exactly:
- 3 short insights (1 sentence each)
- 2 practical saving tips or scheme suggestions

Be friendly, positive, and specific to the numbers/categories.
"""
        return model.generate_content(prompt).text.strip()

    except Exception as e:
        logger.error(f"Insights failed: {e}")
        return None


# ────────────────────────────────────────────────
# MISSING FUNCTION – THIS IS WHAT WAS CAUSING THE ERROR
# ────────────────────────────────────────────────
def generate_scheme_insights(aggregate_text: str):
    if not ENABLE_AI:
        return "AI is disabled."

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
You are a government scheme advisor for panchayat-level families.

Aggregate expense data from all houses:
{aggregate_text}

Suggest 3–4 relevant Indian government schemes that could help these families (e.g., PM Garib Kalyan Anna Yojana for high food expenses, PMAY for housing, Ayushman Bharat for health, etc.).

For each scheme:
- Name of scheme
- Brief why it fits (link to category)
- How to apply or key benefit

Be concise, accurate and useful.
"""
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        logger.error(f"Scheme insights failed: {e}")
        return "Could not generate scheme suggestions at the moment."
import re
from datetime import datetime

# Keyword → (category, subcategory) mapping
CATEGORY_MAP = {
    r"grocer|ration|veg|fruit|milk|rice|dal|oil|kirana": ("Food", "Groceries"),
    r"restau|dining|hotel|food|eat out|cafe|swiggy|zomato|order food": ("Food", "Dining Out"),
    r"snack|chai|coffee|tea|cold drink": ("Food", "Snacks & Beverages"),
    
    r"rent|house rent|monthly rent": ("Housing", "Rent"),
    r"electri|light bill|power bill|eb bill": ("Housing", "Electricity"),
    r"water|gas|cylinder|maintenance|repair|fix|plumb": ("Housing", "Utilities & Maintenance"),
    
    r"fuel|petrol|diesel|bike|car|auto|rickshaw|taxi|uber|ola": ("Transportation", "Fuel & Travel"),
    r"bus|train|metro|ticket|travel": ("Transportation", "Public Transport"),
    
    r"medi|doctor|hospital|clinic|medical|health|pharma": ("Health", "Medicine & Consultation"),
    r"insur|health insu": ("Health", "Insurance"),
    
    r"movie|cinema|theatre|netflix|prime|hotstar|ott|subscr": ("Entertainment", "Movies & Streaming"),
    r"event|concert|party|function": ("Entertainment", "Events"),
    
    r"salary|wage|pay|bonus|credit|income|received": ("Income", "Salary / Wages"),
    r"freelance|project|client|payment received": ("Income", "Freelance / Projects"),
    
    r"phone|mobile|recharge|internet|broadband|wifi": ("Utilities", "Mobile & Internet"),
    r"shop|clothes|dress|shopping": ("Personal", "Shopping"),
    r"gift|donation|charity": ("Personal", "Gifts & Donations"),
    
    # Catch-all
    r".*": ("General", "General")  # last resort
}

def fallback_parse(message: str):
    message_lower = message.lower()

    # Extract amount
    amount_match = re.search(r'(\d+(?:\.\d+)?)', message_lower)
    if not amount_match:
        return None
    amount = float(amount_match.group(1))

    # Determine type
    income_words = ["income", "received", "salary", "bonus", "credit", "got paid"]
    is_income = any(word in message_lower for word in income_words)
    txn_type = "Income" if is_income else "Expense"

    # Find best matching category
    category, subcategory = "General", "General"
    for pattern, (cat, sub) in CATEGORY_MAP.items():
        if re.search(pattern, message_lower):
            category, subcategory = cat, sub
            break  # first match wins

    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": txn_type,
        "amount": amount,
        "category": category,
        "subcategory": subcategory,
        "description": message.strip()
    }
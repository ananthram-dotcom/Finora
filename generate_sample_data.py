import random
from datetime import datetime, timedelta
from services.sheets_service import append_transaction  # Import real append function

# Categories and subcategories
categories = {
    "Food": ["Groceries", "Dining Out", "Snacks"],
    "Housing": ["Rent", "Utilities", "Maintenance"],
    "Transportation": ["Fuel", "Public Transport", "Vehicle Maintenance"],
    "Health": ["Medicine", "Doctor Visits", "Insurance"],
    "Entertainment": ["Movies", "Subscriptions", "Events"],
    "Income": ["Salary", "Freelance", "Investments"]
}

# Generate 100 houses
houses = [f"{i}/100" for i in range(1, 101)]

# For each house, generate 5-15 random transactions
for house in houses:
    num_txns = random.randint(5, 15)
    for _ in range(num_txns):
        date = datetime.now() - timedelta(days=random.randint(0, 365))
        txn_type = random.choice(["Income", "Expense"])
        if txn_type == "Income":
            category = "Income"
            subcategory = random.choice(categories["Income"])
        else:
            category = random.choice(list(categories.keys())[:-1])  # Exclude Income
            subcategory = random.choice(categories[category])
        amount = round(random.uniform(100, 5000), 2)
        description = f"Random {subcategory} transaction"
        
        txn = {
            "house_no": house,
            "date": date.strftime("%Y-%m-%d"),
            "type": txn_type,
            "amount": amount,
            "category": category,
            "subcategory": subcategory,
            "description": description
        }
        append_transaction(txn)

print(f"Generated and appended transactions for 100 houses.")
def validate_transaction(txn: dict):
    required = ["house_no", "date", "type", "amount", "category", "description"]
    for field in required:
        if field not in txn or txn[field] in [None, ""]:
            return False, f"Missing field: {field}"
    if txn["amount"] <= 0:
        return False, "Amount must be positive"
    return True, "Valid"
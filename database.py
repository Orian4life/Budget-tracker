import json
import os
from datetime import datetime

DATA_FILE = "data.json"


class BudgetDatabase:
    def __init__(self):
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as f:
                json.dump({"transactions": []}, f)
        self.data = self.load_data()

    def load_data(self):
        with open(DATA_FILE, "r") as f:
            return json.load(f)

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_transaction(self, amount, category, note):
        self.data["transactions"].append({
            "amount": amount,
            "category": category,
            "note": note,
            "date": datetime.now().strftime("%Y-%m-%d")
        })
        self.save_data()

    def delete_transaction(self, index):
        if 0 <= index < len(self.data["transactions"]):
            self.data["transactions"].pop(index)
            self.save_data()

    def edit_transaction(self, index, amount, category, note):
        if 0 <= index < len(self.data["transactions"]):
            self.data["transactions"][index]["amount"] = amount
            self.data["transactions"][index]["category"] = category
            self.data["transactions"][index]["note"] = note
            self.save_data()

    def get_monthly_total(self):
        month = datetime.now().strftime("%Y-%m")
        total = 0
        for t in self.data["transactions"]:
            if t["date"].startswith(month):
                total += t["amount"]
        return total

    def get_category_summary(self):
        summary = {}
        for t in self.data["transactions"]:
            summary[t["category"]] = summary.get(t["category"], 0) + t["amount"]
        return summary

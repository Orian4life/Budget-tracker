import json
import os

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(expenses):
    with open(DATA_FILE, "w") as f:
        json.dump(expenses, f, indent=4)

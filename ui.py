import tkinter as tk
from tkinter import ttk, messagebox
from database import load_data, save_data

class BudgetApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Budget Tracker")
        self.geometry("400x500")
        self.resizable(False, False)

        self.expenses = load_data()

        self.create_widgets()
        self.update_list()

    def create_widgets(self):
        title = ttk.Label(self, text="Budget Tracker", font=("Arial", 18))
        title.pack(pady=10)

        # Amount
        ttk.Label(self, text="Amount").pack()
        self.amount_entry = ttk.Entry(self)
        self.amount_entry.pack(pady=5)

        # Category
        ttk.Label(self, text="Category").pack()
        self.category_entry = ttk.Entry(self)
        self.category_entry.pack(pady=5)

        # Add button
        add_btn = ttk.Button(self, text="Add Expense", command=self.add_expense)
        add_btn.pack(pady=10)

        # List of expenses
        self.listbox = tk.Listbox(self, height=15)
        self.listbox.pack(fill="both", padx=10, pady=10)

    def add_expense(self):
        amount = self.amount_entry.get()
        category = self.category_entry.get()

        if not amount or not category:
            messagebox.showerror("Error", "Please enter both fields")
            return

        try:
            amount = float(amount)
        except:
            messagebox.showerror("Error", "Amount must be a number")
            return

        self.expenses.append({
            "amount": amount,
            "category": category
        })

        save_data(self.expenses)
        self.update_list()

        # clear fields
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)

    def update_list(self):
        self.listbox.delete(0, tk.END)
        for item in self.expenses:
            self.listbox.insert(tk.END, f"{item['category']} - ₹{item['amount']}")

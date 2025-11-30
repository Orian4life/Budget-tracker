import tkinter as tk
from tkinter import ttk, messagebox
from database import BudgetDatabase
import matplotlib.pyplot as plt


class BudgetApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Budget Tracker")
        self.geometry("650x500")
        self.configure(bg="#121212")

        self.db = BudgetDatabase()

        self.create_styles()
        self.create_ui()
        self.load_table()
        self.update_monthly_total()

    def create_styles(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure("Treeview",
                        background="#1e1e1e",
                        foreground="white",
                        rowheight=28,
                        fieldbackground="#1e1e1e",
                        bordercolor="#333")
        style.map('Treeview', background=[('selected', '#333')])

        style.configure("TButton",
                        padding=6,
                        background="#333",
                        foreground="white")

        style.configure("TLabel",
                        background="#121212",
                        foreground="white")

        style.configure("TEntry",
                        fieldbackground="#1e1e1e",
                        foreground="white")

    def create_ui(self):
        # --- Input Fields ---
        tk.Label(self, text="Amount:", bg="#121212", fg="white").place(x=20, y=20)
        self.amount_entry = ttk.Entry(self, width=15)
        self.amount_entry.place(x=100, y=20)

        tk.Label(self, text="Category:", bg="#121212", fg="white").place(x=20, y=60)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(self, textvariable=self.category_var,
                                              values=["Food", "Travel", "Shopping", "Bills", "Other"],
                                              state="readonly")
        self.category_dropdown.place(x=100, y=60)

        tk.Label(self, text="Note:", bg="#121212", fg="white").place(x=20, y=100)
        self.note_entry = ttk.Entry(self, width=25)
        self.note_entry.place(x=100, y=100)

        ttk.Button(self, text="Add", command=self.add_transaction).place(x=300, y=20)
        ttk.Button(self, text="Edit", command=self.edit_selected).place(x=300, y=60)
        ttk.Button(self, text="Delete", command=self.delete_selected).place(x=300, y=100)

        ttk.Button(self, text="Show Chart", command=self.show_chart).place(x=400, y=60)

        # --- Monthly Total ---
        self.monthly_label = tk.Label(self, text="", font=("Arial", 12), bg="#121212", fg="#00ff88")
        self.monthly_label.place(x=20, y=150)

        # --- Table ---
        self.table = ttk.Treeview(self, columns=("Amount", "Category", "Note", "Date"), show="headings")
        self.table.heading("Amount", text="Amount")
        self.table.heading("Category", text="Category")
        self.table.heading("Note", text="Note")
        self.table.heading("Date", text="Date")
        self.table.place(x=20, y=180, width=600, height=300)

    def load_table(self):
        for row in self.table.get_children():
            self.table.delete(row)

        for t in self.db.data["transactions"]:
            self.table.insert("", "end", values=(t["amount"], t["category"], t["note"], t["date"]))

    def update_monthly_total(self):
        total = self.db.get_monthly_total()
        self.monthly_label.config(text=f"Monthly Total: ₹{total}")

    def add_transaction(self):
        try:
            amount = float(self.amount_entry.get())
        except:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        category = self.category_var.get()
        note = self.note_entry.get()

        if not category:
            messagebox.showerror("Error", "Select a category.")
            return

        self.db.add_transaction(amount, category, note)
        self.load_table()
        self.update_monthly_total()

    def delete_selected(self):
        selected = self.table.selection()
        if not selected:
            return

        index = self.table.index(selected[0])
        self.db.delete_transaction(index)
        self.load_table()
        self.update_monthly_total()

    def edit_selected(self):
        selected = self.table.selection()
        if not selected:
            return

        index = self.table.index(selected[0])

        try:
            amount = float(self.amount_entry.get())
        except:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        category = self.category_var.get()
        note = self.note_entry.get()

        self.db.edit_transaction(index, amount, category, note)
        self.load_table()
        self.update_monthly_total()

    def show_chart(self):
        summary = self.db.get_category_summary()
        if not summary:
            messagebox.showinfo("Info", "No data to show.")
            return

        categories = list(summary.keys())
        values = list(summary.values())

        plt.pie(values, labels=categories, autopct="%1.1f%%")
        plt.title("Expense Category Distribution")
        plt.show()

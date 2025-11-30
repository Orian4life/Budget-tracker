import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
import matplotlib.pyplot as plt
from database import BudgetDatabase


class BudgetApp(tb.Window):
    def __init__(self):
        super().__init__(themename="cosmo")

        self.title("Budget Tracker")
        self.geometry("900x550")

        self.db = BudgetDatabase()
        self.selected_index = None  # Track selected table row

        self.create_ui()
        self.load_table()
        self.update_monthly_total()

    # ----------------------------------------------------------
    # UI DESIGN
    # ----------------------------------------------------------
    def create_ui(self):

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---------------- LEFT PANEL ----------------
        left = tb.Frame(self, padding=15)
        left.grid(row=0, column=0, sticky="ns")

        # Amount input
        tb.Label(left, text="Amount:", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w")
        self.amount_entry = tb.Entry(left, width=18)
        self.amount_entry.grid(row=1, column=0, pady=5)

        # Category input
        tb.Label(left, text="Category:", font=("Segoe UI", 11)).grid(row=2, column=0, sticky="w")
        self.category_var = tb.StringVar()
        self.category = tb.Combobox(
            left,
            textvariable=self.category_var,
            values=["Food", "Travel", "Shopping", "Bills", "Other"],
            width=16,
            state="readonly"
        )
        self.category.grid(row=3, column=0, pady=5)

        # Note input
        tb.Label(left, text="Note:", font=("Segoe UI", 11)).grid(row=4, column=0, sticky="w")
        self.note_entry = tb.Entry(left, width=18)
        self.note_entry.grid(row=5, column=0, pady=5)

        # Buttons
        tb.Button(left, text="Add", bootstyle=SUCCESS, command=self.add_transaction).grid(row=6, column=0, pady=8, sticky="ew")
        tb.Button(left, text="Edit", bootstyle=INFO, command=self.edit_selected).grid(row=7, column=0, pady=8, sticky="ew")
        tb.Button(left, text="Delete", bootstyle=DANGER, command=self.delete_selected).grid(row=8, column=0, pady=8, sticky="ew")
        tb.Button(left, text="Show Chart", bootstyle=SECONDARY, command=self.show_chart).grid(row=9, column=0, pady=15, sticky="ew")

        # Monthly total label
        self.monthly_label = tb.Label(left, text="", font=("Segoe UI", 12, "bold"), bootstyle=SUCCESS)
        self.monthly_label.grid(row=10, column=0, pady=10)

        # ---------------- TABLE ----------------
        table_frame = tb.Frame(self, padding=10)
        table_frame.grid(row=0, column=1, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        self.table = tb.Treeview(
            table_frame,
            columns=("Amount", "Category", "Note", "Date"),
            show="headings",
            bootstyle=PRIMARY
        )

        for col in ("Amount", "Category", "Note", "Date"):
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center")

        self.table.grid(row=0, column=0, sticky="nsew")

        scrollbar = tb.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Bind row click
        self.table.bind("<<TreeviewSelect>>", self.on_row_select)

    # ----------------------------------------------------------
    # DATA FUNCTIONS
    # ----------------------------------------------------------
    def load_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for t in self.db.data["transactions"]:
            self.table.insert("", "end", values=(t["amount"], t["category"], t["note"], t["date"]))

    def update_monthly_total(self):
        total = self.db.get_monthly_total()
        self.monthly_label.config(text=f"Monthly Total: ₹{total}")

    # Clear all input fields
    def clear_inputs(self):
        self.amount_entry.delete(0, "end")
        self.note_entry.delete(0, "end")
        self.category_var.set("")
        self.selected_index = None

    # ----------------------------------------------------------
    # BUTTON FUNCTIONS
    # ----------------------------------------------------------
    def add_transaction(self):
        try:
            amount = float(self.amount_entry.get())
        except:
            messagebox.showerror("Invalid Input", "Amount must be a number.")
            return

        category = self.category_var.get()
        note = self.note_entry.get()

        if not category:
            messagebox.showwarning("Missing Data", "Select a category.")
            return

        self.db.add_transaction(amount, category, note)
        self.load_table()
        self.update_monthly_total()
        self.clear_inputs()

    def on_row_select(self, event):
        selected = self.table.selection()
        if not selected:
            return

        values = self.table.item(selected[0])["values"]
        self.selected_index = self.table.index(selected[0])

        self.amount_entry.delete(0, "end")
        self.amount_entry.insert(0, values[0])

        self.category_var.set(values[1])

        self.note_entry.delete(0, "end")
        self.note_entry.insert(0, values[2])

    def edit_selected(self):
        if self.selected_index is None:
            messagebox.showerror("Error", "Select a row first.")
            return

        try:
            amount = float(self.amount_entry.get())
        except:
            messagebox.showerror("Invalid Input", "Amount must be a number.")
            return

        category = self.category_var.get()
        note = self.note_entry.get()

        self.db.edit_transaction(self.selected_index, amount, category, note)
        self.load_table()
        self.update_monthly_total()
        self.clear_inputs()

    def delete_selected(self):
        if self.selected_index is None:
            messagebox.showerror("Error", "Select a row first.")
            return

        self.db.delete_transaction(self.selected_index)
        self.load_table()
        self.update_monthly_total()
        self.clear_inputs()

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

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
import matplotlib.pyplot as plt
from database import BudgetDatabase # Assuming this file exists and works

class BudgetApp(tb.Window):
    def __init__(self):
        super().__init__(themename="cosmo")

        self.title("Budget Tracker 💰")
        # Increased initial size for better layout
        self.geometry("1000x600")

        self.db = BudgetDatabase()
        self.selected_index = None  # Track selected table row

        self.create_ui()
        self.load_table()
        self.update_monthly_total()

    # ----------------------------------------------------------
    # UI DESIGN
    # ----------------------------------------------------------
    def create_ui(self):
        # Use a Notebook for tabbed interface
        self.notebook = tb.Notebook(self)
        self.notebook.pack(pady=10, padx=10, fill=BOTH, expand=True)

        # --- Tab 1: Transactions ---
        transaction_tab = tb.Frame(self.notebook)
        self.notebook.add(transaction_tab, text="Transactions 📝")

        # Layout for the Transaction Tab
        transaction_tab.grid_columnconfigure(1, weight=1)
        transaction_tab.grid_rowconfigure(0, weight=1)

        # ---------------- LEFT PANEL (Input Controls) ----------------
        # Use a Labelframe for a cleaner grouping of inputs
        input_frame = tb.Labelframe(transaction_tab, text="New/Edit Transaction", padding=20, bootstyle=PRIMARY)
        input_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        # Amount input
        tb.Label(input_frame, text="Amount:", font=("Segoe UI", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.amount_entry = tb.Entry(input_frame, width=25, bootstyle=INFO)
        self.amount_entry.grid(row=1, column=0, pady=(0, 15), padx=5)

        # Category input
        tb.Label(input_frame, text="Category:", font=("Segoe UI", 12)).grid(row=2, column=0, sticky="w", pady=5)
        self.category_var = tb.StringVar()
        self.category = tb.Combobox(
            input_frame,
            textvariable=self.category_var,
            values=["Food", "Travel", "Shopping", "Bills", "Other"],
            width=23,
            state="readonly",
            bootstyle=INFO
        )
        self.category.grid(row=3, column=0, pady=(0, 15), padx=5)

        # Note input
        tb.Label(input_frame, text="Note:", font=("Segoe UI", 12)).grid(row=4, column=0, sticky="w", pady=5)
        self.note_entry = tb.Entry(input_frame, width=25, bootstyle=INFO)
        self.note_entry.grid(row=5, column=0, pady=(0, 20), padx=5)

        # Buttons - Used `Grid` for a stacked look with better spacing
        tb.Button(input_frame, text="➕ Add Transaction", bootstyle=SUCCESS, command=self.add_transaction).grid(row=6, column=0, pady=8, sticky="ew")
        tb.Button(input_frame, text="✏️ Edit Selected", bootstyle=INFO, command=self.edit_selected).grid(row=7, column=0, pady=8, sticky="ew")
        tb.Button(input_frame, text="❌ Delete Selected", bootstyle=DANGER, command=self.delete_selected).grid(row=8, column=0, pady=8, sticky="ew")
        
        # Monthly total label - Moved it below the buttons
        self.monthly_label = tb.Label(input_frame, text="", font=("Segoe UI", 14, "bold"), bootstyle=SUCCESS)
        self.monthly_label.grid(row=9, column=0, pady=(20, 5))


        # ---------------- TABLE (Display) ----------------
        table_frame = tb.Frame(transaction_tab, padding=5)
        table_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        self.table = tb.Treeview(
            table_frame,
            columns=("Amount", "Category", "Note", "Date"),
            show="headings",
            bootstyle=PRIMARY,
            height=15 # Set a default height for better look
        )

        for col in ("Amount", "Category", "Note", "Date"):
            # Set relative widths for columns
            if col == "Date":
                width = 150
            elif col == "Note":
                width = 250
            else:
                width = 100

            self.table.heading(col, text=col)
            self.table.column(col, anchor="center", width=width, stretch=True)

        self.table.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = tb.Scrollbar(table_frame, orient="vertical", command=self.table.yview, bootstyle=PRIMARY)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Bind row click
        self.table.bind("<<TreeviewSelect>>", self.on_row_select)

        # --- Tab 2: Chart ---
        chart_tab = tb.Frame(self.notebook)
        self.notebook.add(chart_tab, text="Summary Chart 📈")
        
        # A button to show the chart is now inside the chart tab
        tb.Button(chart_tab, text="View Expense Chart", bootstyle=SECONDARY, command=self.show_chart_in_tab).pack(pady=50, padx=20)


    # ----------------------------------------------------------
    # DATA FUNCTIONS (Unchanged)
    # ----------------------------------------------------------
    def load_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for t in self.db.data["transactions"]:
            self.table.insert("", "end", values=(f'₹{t["amount"]:.2f}', t["category"], t["note"], t["date"])) # Added rupee symbol and formatting

    def update_monthly_total(self):
        total = self.db.get_monthly_total()
        self.monthly_label.config(text=f"Monthly Total:\n₹{total:.2f}")

    # Clear all input fields
    def clear_inputs(self):
        self.amount_entry.delete(0, "end")
        self.note_entry.delete(0, "end")
        self.category_var.set("")
        self.selected_index = None

    # ----------------------------------------------------------
    # BUTTON FUNCTIONS (Modified to call new chart function)
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

        # The values retrieved here might include the '₹' symbol from load_table,
        # so we need to strip it before inserting back into the amount field.
        values = self.table.item(selected[0])["values"]
        
        # Determine the correct index based on the actual transaction list (used in edit/delete)
        # Note: self.table.index is for Treeview row position, NOT the DB index.
        # We'll rely on the position, assuming the list order matches the DB's internal order.
        self.selected_index = self.table.index(selected[0])

        self.amount_entry.delete(0, "end")
        # Strip currency symbol and re-insert the numerical value
        amount_str = str(values[0]).replace('₹', '')
        self.amount_entry.insert(0, amount_str) 

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

    # The original function is renamed and modified to be called from the chart tab
    def show_chart_in_tab(self):
        self.show_chart()

    def show_chart(self):
        summary = self.db.get_category_summary()

        if not summary:
            messagebox.showinfo("Info", "No data to show.")
            # Switch back to transaction tab if no data
            self.notebook.select(0) 
            return

        categories = list(summary.keys())
        values = list(summary.values())

        plt.figure(figsize=(8, 8)) # Set a specific size for a better pie chart look
        plt.pie(values, labels=categories, autopct="%1.1f%%", startangle=90, wedgeprops={'edgecolor': 'black'})
        plt.title("Expense Category Distribution", fontsize=16)
        plt.axis('equal') # Ensures the pie chart is drawn as a circle
        plt.show()

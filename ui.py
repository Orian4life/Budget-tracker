import tkinter as tk
from tkinter import ttk, messagebox
from database import BudgetDatabase
import matplotlib.pyplot as plt


class BudgetApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Budget Tracker")
        self.geometry("780x550")
        self.configure(bg="#0F0F0F")

        self.db = BudgetDatabase()

        self.create_styles()
        self.create_layout()
        self.load_table()
        self.update_monthly_total()

    # ---------------------------- Modern Styles ----------------------------
    def create_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # --- Modern TreeView ---
        style.configure(
            "Treeview",
            background="#1A1A1A",
            foreground="white",
            rowheight=30,
            fieldbackground="#1A1A1A",
            bordercolor="#333",
            font=("Segoe UI", 10)
        )
        style.configure("Treeview.Heading",
                        background="#252525",
                        foreground="#00EFFF",
                        font=("Segoe UI", 11, "bold"))

        style.map("Treeview",
                  background=[("selected", "#003F7F")],
                  foreground=[("selected", "white")])

        # --- Modern Buttons ---
        style.configure("ModernButton.TButton",
                        background="#0078FF",
                        foreground="white",
                        padding=8,
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=0)

        style.map("ModernButton.TButton",
                  background=[("active", "#005FCC")])

        # Labels / Entry
        style.configure("TLabel",
                        background="#111111",
                        foreground="white",
                        font=("Segoe UI", 10))

        style.configure("TEntry",
                        fieldbackground="#1A1A1A",
                        foreground="white")

    # ---------------------------- Layout ----------------------------
    def create_layout(self):

        # Top Header Bar
        header = tk.Frame(self, bg="#0078FF", height=70)
        header.pack(fill="x")

        tk.Label(header, text="💰 Budget Tracker",
                 bg="#0078FF", fg="white",
                 font=("Segoe UI", 20, "bold")).pack(pady=10)

        # Main Layout
        main_frame = tk.Frame(self, bg="#0F0F0F")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Left Card (Inputs)
        input_card = tk.Frame(main_frame, bg="#151515", bd=1, relief="solid")
        input_card.place(x=0, y=0, width=300, height=450)

        tk.Label(input_card, text="Amount").place(x=20, y=20)
        self.amount_entry = ttk.Entry(input_card, width=20)
        self.amount_entry.place(x=120, y=20)

        tk.Label(input_card, text="Category").place(x=20, y=70)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(
            input_card, textvariable=self.category_var,
            values=["Food", "Travel", "Shopping", "Bills", "Other"],
            state="readonly"
        )
        self.category_dropdown.place(x=120, y=70)

        tk.Label(input_card, text="Note").place(x=20, y=120)
        self.note_entry = ttk.Entry(input_card, width=20)
        self.note_entry.place(x=120, y=120)

        ttk.Button(input_card, text="Add",
                   command=self.add_transaction, style="ModernButton.TButton"
                   ).place(x=20, y=180, width=240)

        ttk.Button(input_card, text="Edit",
                   command=self.edit_selected, style="ModernButton.TButton"
                   ).place(x=20, y=225, width=240)

        ttk.Button(input_card, text="Delete",
                   command=self.delete_selected, style="ModernButton.TButton"
                   ).place(x=20, y=270, width=240)

        ttk.Button(input_card, text="Show Chart",
                   command=self.show_chart, style="ModernButton.TButton"
                   ).place(x=20, y=315, width=240)

        # Monthly total label
        self.monthly_label = tk.Label(input_card,
                                      text="Monthly Total: ₹0",
                                      font=("Segoe UI", 12, "bold"),
                                      fg="#00FFAA", bg="#151515")
        self.monthly_label.place(x=20, y=380)

        # Right Table
        self.table = ttk.Treeview(main_frame,
                                  columns=("Amount", "Category", "Note", "Date"),
                                  show="headings")

        for col in ("Amount", "Category", "Note", "Date"):
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center")

        self.table.place(x=320, y=0, width=430, height=450)

    # ---------------------------- Functions ----------------------------
    def load_table(self):
        for row in self.table.get_children():
            self.table.delete(row)

        for t in self.db.data["transactions"]:
            self.table.insert("", "end",
                              values=(t["amount"], t["category"], t["note"], t["date"]))

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

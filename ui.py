import tkinter as tk
from tkinter import ttk, messagebox
from database import BudgetDatabase
import matplotlib.pyplot as plt


ACCENT = "#1E90FF"   # Neon Blue
BG_DARK = "#0f0f0f"
CARD = "#1a1a1a"
TEXT = "#ffffff"
SUCCESS = "#00e676"


class BudgetApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Budget Tracker")
        self.geometry("900x600")
        self.configure(bg=BG_DARK)

        self.db = BudgetDatabase()

        self.setup_styles()
        self.build_topbar()
        self.build_layout()
        self.load_table()
        self.update_monthly_total()

    # ------------------------------------------------
    # MODERN STYLING
    # ------------------------------------------------
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TLabel",
                        background=BG_DARK,
                        foreground=TEXT,
                        font=("Segoe UI", 10))

        style.configure("TEntry",
                        padding=5,
                        fieldbackground=CARD,
                        foreground=TEXT)

        style.configure("TButton",
                        font=("Segoe UI", 10, "bold"),
                        padding=8,
                        background=ACCENT,
                        foreground="white",
                        borderwidth=0)

        style.map("TButton",
                  background=[("active", "#0b63c3")])

        style.configure("Treeview",
                        background=CARD,
                        foreground=TEXT,
                        rowheight=30,
                        fieldbackground=CARD,
                        bordercolor="#333333",
                        borderwidth=0)

        style.configure("Treeview.Heading",
                        font=("Segoe UI", 11, "bold"),
                        background="#222222",
                        foreground="#1E90FF")

    # ------------------------------------------------
    # TOP BAR
    # ------------------------------------------------
    def build_topbar(self):
        topbar = tk.Frame(self, bg=ACCENT, height=60)
        topbar.pack(fill="x", side="top")

        tk.Label(topbar,
                 text="💰  Budget Tracker",
                 font=("Segoe UI", 20, "bold"),
                 bg=ACCENT,
                 fg="white").pack(pady=10)

    # ------------------------------------------------
    # PAGE LAYOUT
    # ------------------------------------------------
    def build_layout(self):
        container = tk.Frame(self, bg=BG_DARK)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # LEFT FORM CARD
        form = tk.Frame(container, bg=CARD, bd=1, relief="solid")
        form.place(x=0, y=0, width=260, height=500)

        # Inputs
        tk.Label(form, text="Amount:", bg=CARD).place(x=20, y=30)
        self.amount_entry = ttk.Entry(form, width=20)
        self.amount_entry.place(x=100, y=30)

        tk.Label(form, text="Category:", bg=CARD).place(x=20, y=80)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(
            form, textvariable=self.category_var,
            values=["Food", "Travel", "Shopping", "Bills", "Other"],
            state="readonly"
        )
        self.category_dropdown.place(x=100, y=80)

        tk.Label(form, text="Note:", bg=CARD).place(x=20, y=130)
        self.note_entry = ttk.Entry(form, width=22)
        self.note_entry.place(x=100, y=130)

        # Buttons
        ttk.Button(form, text="Add", command=self.add_transaction).place(x=70, y=200, width=120)
        ttk.Button(form, text="Edit", command=self.edit_selected).place(x=70, y=250, width=120)
        ttk.Button(form, text="Delete", command=self.delete_selected).place(x=70, y=300, width=120)
        ttk.Button(form, text="Show Chart", command=self.show_chart).place(x=70, y=350, width=120)

        # Monthly Total
        self.monthly_label = tk.Label(form, text="", font=("Segoe UI", 12, "bold"),
                                      bg=CARD, fg=SUCCESS)
        self.monthly_label.place(x=20, y=420)

        # ------------------------
        # TABLE AREA
        # ------------------------
        table_frame = tk.Frame(container, bg=BG_DARK)
        table_frame.place(x=280, y=0, width=580, height=500)

        self.table = ttk.Treeview(
            table_frame,
            columns=("Amount", "Category", "Note", "Date"),
            show="headings"
        )

        for col in ("Amount", "Category", "Note", "Date"):
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center")

        self.table.pack(fill="both", expand=True)

    # ------------------------------------------------
    # LOGIC
    # ------------------------------------------------
    def load_table(self):
        self.table.delete(*self.table.get_children())
        for t in self.db.data["transactions"]:
            self.table.insert("", "end", values=(
                t["amount"], t["category"], t["note"], t["date"]
            ))

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

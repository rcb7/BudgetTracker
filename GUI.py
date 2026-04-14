import sys
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.insert(0, r"e:\Python\BudgetTracker")
from budget import BudgetTracker, Expense, PERSONAL_USE, JOINT_USE

# --- Colours & fonts ---
BG         = "#1e1e2e"
SURFACE    = "#2a2a3d"
ACCENT     = "#7c6af7"
ACCENT_HOV = "#6a58e0"
DANGER     = "#e05c6a"
DANGER_HOV = "#c94d5a"
SUCCESS    = "#50c878"
TEXT       = "#e0e0f0"
SUBTEXT    = "#9999bb"
ROW_ODD    = "#25253a"
ROW_EVEN   = "#2e2e45"

FONT       = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_SMALL = ("Segoe UI", 9)

tracker = BudgetTracker()
tracker.load_expenses()
tracker.load_budget()

# --- Helpers ---

def refresh_table():
    for row in table.get_children():
        table.delete(row)
    for i, e in enumerate(tracker.expenses):
        tag = "odd" if i % 2 == 0 else "even"
        table.insert("", "end", iid=i, tags=(tag,),
                     values=(e.date, e.description, f"${e.amount:.2f}", e.use, e.category))
    update_status()

def update_status():
    total = tracker.total_expenses()
    if tracker.budget is not None:
        remaining = tracker.budget - total
        color = SUCCESS if remaining >= 0 else DANGER
        status_var.set(f"  Budget: ${tracker.budget:.2f}     Spent: ${total:.2f}     Remaining: ${remaining:.2f}")
        status_label.config(fg=color)
    else:
        status_var.set(f"  Budget: Not set     Spent: ${total:.2f}")
        status_label.config(fg=SUBTEXT)

def save_all():
    tracker.save_expenses()
    tracker.save_budget()

def save_and_exit():
    save_all()
    window.destroy()

# --- Styled dialog base ---

def make_dialog(title):
    dialog = tk.Toplevel(window)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.configure(bg=BG)
    dialog.grab_set()
    tk.Label(dialog, text=title, font=FONT_TITLE, bg=BG, fg=TEXT).grid(
        row=0, column=0, columnspan=2, pady=(16, 8), padx=20)
    return dialog

def styled_label(parent, text, row):
    tk.Label(parent, text=text, font=FONT, bg=BG, fg=SUBTEXT, anchor="w").grid(
        row=row, column=0, padx=(20, 8), pady=5, sticky="w")

def styled_entry(parent, row, value=""):
    entry = tk.Entry(parent, width=26, font=FONT, bg=SURFACE, fg=TEXT,
                     insertbackground=TEXT, relief="flat", bd=6)
    entry.grid(row=row, column=1, padx=(0, 20), pady=5)
    entry.insert(0, value)
    return entry

def styled_button(parent, text, command, color=ACCENT, hover=ACCENT_HOV, **kwargs):
    btn = tk.Button(parent, text=text, command=command, font=FONT_BOLD,
                    bg=color, fg="white", activebackground=hover,
                    activeforeground="white", relief="flat", cursor="hand2",
                    padx=14, pady=6, bd=0, **kwargs)
    btn.bind("<Enter>", lambda _: btn.config(bg=hover))
    btn.bind("<Leave>", lambda _: btn.config(bg=color))
    return btn

# --- Add Expense ---

def open_add_dialog():
    dialog = make_dialog("Add Expense")
    field_defs = ["Date (YYYY-MM-DD)", "Description", "Amount", "Category"]
    fields = {}
    for i, label in enumerate(field_defs):
        styled_label(dialog, label, i + 1)
        fields[label] = styled_entry(dialog, i + 1)

    row = len(field_defs) + 1
    styled_label(dialog, "Use", row)
    use_var = tk.StringVar(value=PERSONAL_USE)
    use_menu = ttk.Combobox(dialog, textvariable=use_var, values=[PERSONAL_USE, JOINT_USE],
                             state="readonly", width=23, font=FONT)
    use_menu.grid(row=row, column=1, padx=(0, 20), pady=5)

    def submit():
        try:
            date        = fields["Date (YYYY-MM-DD)"].get().strip()
            description = fields["Description"].get().strip()
            amount      = float(fields["Amount"].get().strip())
            category    = fields["Category"].get().strip()
            use         = use_var.get()
            if not date or not description or not category:
                messagebox.showerror("Error", "All fields are required.", parent=dialog)
                return
            tracker.add_expense(Expense(date, description, amount, use, category))
            refresh_table()
            save_all()
            dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.", parent=dialog)

    styled_button(dialog, "Add Expense", submit).grid(
        row=row + 1, column=0, columnspan=2, pady=(12, 18))

# --- Remove Expense ---

def remove_expense():
    selected = table.selection()
    if not selected:
        messagebox.showwarning("No selection", "Select an expense to remove.")
        return
    index = int(selected[0])
    if messagebox.askyesno("Confirm", "Remove selected expense?"):
        tracker.remove_expense(index)
        refresh_table()
        save_all()

# --- Edit Expense ---

def open_edit_dialog():
    selected = table.selection()
    if not selected:
        messagebox.showwarning("No selection", "Select an expense to edit.")
        return
    index   = int(selected[0])
    expense = tracker.expenses[index]

    dialog = make_dialog("Edit Expense")
    field_defs = [
        ("Date (YYYY-MM-DD)", expense.date),
        ("Description",       expense.description),
        ("Amount",            str(expense.amount)),
        ("Category",          expense.category),
    ]
    fields = {}
    for i, (label, value) in enumerate(field_defs):
        styled_label(dialog, label, i + 1)
        fields[label] = styled_entry(dialog, i + 1, value)

    row = len(field_defs) + 1
    styled_label(dialog, "Use", row)
    use_var = tk.StringVar(value=expense.use)
    use_menu = ttk.Combobox(dialog, textvariable=use_var, values=[PERSONAL_USE, JOINT_USE],
                             state="readonly", width=23, font=FONT)
    use_menu.grid(row=row, column=1, padx=(0, 20), pady=5)

    def submit():
        try:
            date        = fields["Date (YYYY-MM-DD)"].get().strip()
            description = fields["Description"].get().strip()
            amount      = float(fields["Amount"].get().strip())
            category    = fields["Category"].get().strip()
            use         = use_var.get()
            if not date or not description or not category:
                messagebox.showerror("Error", "All fields are required.", parent=dialog)
                return
            tracker.edit_expense(index, date, description, amount, use, category)
            refresh_table()
            save_all()
            dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.", parent=dialog)

    styled_button(dialog, "Save Changes", submit).grid(
        row=row + 1, column=0, columnspan=2, pady=(12, 18))

# --- Set Budget ---

def open_budget_dialog():
    dialog = make_dialog("Set Budget")
    styled_label(dialog, "Budget amount:", 1)
    entry = styled_entry(dialog, 1, str(tracker.budget) if tracker.budget is not None else "")

    def submit():
        try:
            amount = float(entry.get().strip())
            tracker.set_budget(amount)
            save_all()
            update_status()
            dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.", parent=dialog)

    styled_button(dialog, "Set Budget", submit).grid(
        row=2, column=0, columnspan=2, pady=(12, 18))

# --- Window ---

window = tk.Tk()
window.title("Budget Tracker")
window.configure(bg=BG)
window.resizable(False, False)

# Title bar
title_bar = tk.Frame(window, bg=BG)
title_bar.pack(fill="x", padx=20, pady=(16, 4))
tk.Label(title_bar, text="Budget Tracker", font=FONT_TITLE, bg=BG, fg=TEXT).pack(side="left")

# Toolbar
toolbar = tk.Frame(window, bg=BG)
toolbar.pack(fill="x", padx=20, pady=(6, 4))

styled_button(toolbar, "+ Add",    open_add_dialog).pack(side="left", padx=(0, 6))
styled_button(toolbar, "✎ Edit",   open_edit_dialog).pack(side="left", padx=(0, 6))
styled_button(toolbar, "✕ Remove", remove_expense, color=DANGER, hover=DANGER_HOV).pack(side="left", padx=(0, 6))
styled_button(toolbar, "$ Budget", open_budget_dialog).pack(side="left", padx=(0, 6))
styled_button(toolbar, "Save & Exit", save_and_exit, color="#444466", hover="#555580").pack(side="right")

# Divider
tk.Frame(window, bg=ACCENT, height=2).pack(fill="x", padx=20, pady=(4, 0))

# Table
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",
    background=ROW_ODD, foreground=TEXT, fieldbackground=ROW_ODD,
    rowheight=28, font=FONT, borderwidth=0)
style.configure("Treeview.Heading",
    background=SURFACE, foreground=ACCENT, font=FONT_BOLD, relief="flat")
style.map("Treeview",
    background=[("selected", ACCENT)],
    foreground=[("selected", "white")])

columns = ("Date", "Description", "Amount", "Use", "Category")
table = ttk.Treeview(window, columns=columns, show="headings", height=18)
table.tag_configure("odd",  background=ROW_ODD)
table.tag_configure("even", background=ROW_EVEN)

col_widths = {"Date": 110, "Description": 200, "Amount": 90, "Use": 100, "Category": 130}
for col in columns:
    table.heading(col, text=col)
    table.column(col, width=col_widths[col], anchor="center")

scrollbar = ttk.Scrollbar(window, orient="vertical", command=table.yview)
table.configure(yscrollcommand=scrollbar.set)
table.pack(side="left", padx=(20, 0), pady=10)
scrollbar.pack(side="left", fill="y", pady=10)

# Status bar
status_var = tk.StringVar()
status_label = tk.Label(window, textvariable=status_var, font=FONT_SMALL,
                         bg=SURFACE, fg=SUBTEXT, anchor="w", pady=6)
status_label.pack(fill="x", side="bottom", padx=0)

refresh_table()
window.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont

from budget import BudgetTracker, Expense, PERSONAL_USE, JOINT_USE

# --- Colours & fonts ---
BG          = "#303030"
SURFACE     = "#3d3d3d"
ACCENT      = "#7b1832"
ACCENT_HOV  = "#611427"
SUCCESS     = "#5a8a5a"
TEXT        = "#ffffff"
SUBTEXT     = "#aaaaaa"
ROW_ODD     = "#2e2e2e"
ROW_EVEN    = "#383838"
NEUTRAL     = "#555555"
NEUTRAL_HOV = "#686868"

# Pastel toolbar button colours
BTN_ADD     = "#a8d5a2"
BTN_ADD_HOV = "#8ec48a"
BTN_EDIT    = "#a2b8d5"
BTN_EDIT_HOV= "#8aa4c4"
BTN_DEL     = "#d5a2a2"
BTN_DEL_HOV = "#c48a8a"
BTN_BUD     = "#d5a2b8"
BTN_BUD_HOV = "#c48aa4"
BTN_FG      = "#1e1e1e"

FONT       = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_SMALL = ("Segoe UI", 9)

tracker = BudgetTracker()
tracker.load_expenses()
tracker.load_budget()

# --- Rounded button ---

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, color=ACCENT, hover=ACCENT_HOV,
                 fg="white", radius=14, padx=20, pady=9, **kwargs):
        super().__init__(parent, highlightthickness=0, bd=0,
                         bg=parent.cget("bg"), **kwargs)
        self._color   = color
        self._hover   = hover
        self._command = command
        self._radius  = radius

        f  = tkfont.Font(family=FONT_BOLD[0], size=FONT_BOLD[1], weight="bold")
        tw = f.measure(text)
        th = f.metrics("linespace")
        w  = tw + padx * 2
        h  = th + pady * 2

        self.config(width=w, height=h)
        self._rect = self._draw(color, w, h)
        self.create_text(w // 2, h // 2, text=text, fill=fg, font=FONT_BOLD)
        self.bind("<Enter>",           lambda _: self._set(hover))
        self.bind("<Leave>",           lambda _: self._set(color))
        self.bind("<ButtonRelease-1>", lambda _: command())
        self.config(cursor="hand2")

    def _draw(self, color, w, h):
        r = self._radius
        pts = [r,0, w-r,0, w,0, w,r, w,h-r, w,h, w-r,h, r,h, 0,h, 0,h-r, 0,r, 0,0]
        return self.create_polygon(pts, smooth=True, fill=color, outline=color)

    def _set(self, color):
        self.itemconfig(self._rect, fill=color, outline=color)


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
        color = SUCCESS if remaining >= 0 else BTN_DEL
        budget_val.config(text=f"${tracker.budget:.2f}", fg=TEXT)
        spent_val.config(text=f"${total:.2f}", fg=TEXT)
        remaining_val.config(text=f"${remaining:.2f}", fg=color)
    else:
        budget_val.config(text="Not set", fg=SUBTEXT)
        spent_val.config(text=f"${total:.2f}", fg=TEXT)
        remaining_val.config(text="—", fg=SUBTEXT)

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
        row=0, column=0, columnspan=2, pady=(24, 10), padx=28)
    return dialog

def styled_label(parent, text, row):
    tk.Label(parent, text=text, font=FONT, bg=BG, fg=SUBTEXT, anchor="w").grid(
        row=row, column=0, padx=(28, 10), pady=7, sticky="w")

def styled_entry(parent, row, value=""):
    entry = tk.Entry(parent, width=26, font=FONT, bg=SURFACE, fg=TEXT,
                     insertbackground=TEXT, relief="flat", bd=8)
    entry.grid(row=row, column=1, padx=(0, 28), pady=7)
    entry.insert(0, value)
    return entry

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
    use_menu.grid(row=row, column=1, padx=(0, 28), pady=7)

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

    RoundedButton(dialog, "Add Expense", submit).grid(
        row=row + 1, column=0, columnspan=2, pady=(16, 24))

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
    use_menu.grid(row=row, column=1, padx=(0, 28), pady=7)

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

    RoundedButton(dialog, "Save Changes", submit).grid(
        row=row + 1, column=0, columnspan=2, pady=(16, 24))

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

    RoundedButton(dialog, "Set Budget", submit).grid(
        row=2, column=0, columnspan=2, pady=(16, 24))

# --- Window ---

window = tk.Tk()
window.title("Budget Tracker")
window.configure(bg=BG)
window.resizable(False, False)

# --- Header: title left, stat cards right ---
header = tk.Frame(window, bg=BG)
header.pack(fill="x", padx=24, pady=(20, 8))

tk.Label(header, text="Budget Tracker", font=FONT_TITLE, bg=BG, fg=TEXT).pack(side="left")

def stat_card(parent, label_text):
    card = tk.Frame(parent, bg=SURFACE, padx=14, pady=6)
    tk.Label(card, text=label_text, font=FONT_SMALL, bg=SURFACE, fg=SUBTEXT).pack()
    val = tk.Label(card, text="—", font=FONT_BOLD, bg=SURFACE, fg=TEXT)
    val.pack()
    return card, val

stats = tk.Frame(header, bg=BG)
stats.pack(side="right")

remaining_card, remaining_val = stat_card(stats, "Remaining")
remaining_card.pack(side="right", padx=(8, 0))

spent_card, spent_val = stat_card(stats, "Spent")
spent_card.pack(side="right", padx=(8, 0))

budget_card, budget_val = stat_card(stats, "Budget")
budget_card.pack(side="right", padx=(8, 0))

# --- Toolbar ---
toolbar = tk.Frame(window, bg=BG)
toolbar.pack(fill="x", padx=24, pady=(0, 8))

RoundedButton(toolbar, "Add",    open_add_dialog,    color=BTN_ADD,  hover=BTN_ADD_HOV,  fg=BTN_FG).pack(side="left", padx=(0, 8))
RoundedButton(toolbar, "Edit",   open_edit_dialog,   color=BTN_EDIT, hover=BTN_EDIT_HOV, fg=BTN_FG).pack(side="left", padx=(0, 8))
RoundedButton(toolbar, "Remove", remove_expense,     color=BTN_DEL,  hover=BTN_DEL_HOV,  fg=BTN_FG).pack(side="left", padx=(0, 8))
RoundedButton(toolbar, "Budget", open_budget_dialog, color=BTN_BUD,  hover=BTN_BUD_HOV,  fg=BTN_FG).pack(side="left", padx=(0, 8))
RoundedButton(toolbar, "Save & Exit", save_and_exit,     color=NEUTRAL,  hover=NEUTRAL_HOV).pack(side="right")

# Divider
tk.Frame(window, bg=ACCENT, height=2).pack(fill="x", padx=24)

# --- Table ---
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",
    background=ROW_ODD, foreground=TEXT, fieldbackground=ROW_ODD,
    rowheight=32, font=FONT, borderwidth=0)
style.configure("Treeview.Heading",
    background=SURFACE, foreground=TEXT, font=FONT_BOLD, relief="flat")
style.map("Treeview",
    background=[("selected", ACCENT)],
    foreground=[("selected", "white")])

columns = ("Date", "Description", "Amount", "Use", "Category")
table = ttk.Treeview(window, columns=columns, show="headings", height=18)
table.tag_configure("odd",  background=ROW_ODD,  foreground=TEXT)
table.tag_configure("even", background=ROW_EVEN, foreground=TEXT)

col_widths = {"Date": 110, "Description": 200, "Amount": 90, "Use": 100, "Category": 130}
for col in columns:
    table.heading(col, text=col)
    table.column(col, width=col_widths[col], anchor="center")

scrollbar = ttk.Scrollbar(window, orient="vertical", command=table.yview)
table.configure(yscrollcommand=scrollbar.set)
table.pack(side="left", padx=(24, 0), pady=12)
scrollbar.pack(side="left", fill="y", pady=12)

refresh_table()
window.mainloop()

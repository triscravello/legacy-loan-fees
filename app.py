import tkinter as tk
from pathlib import Path
from tkinter import ttk
from legacy import format_report, legacy_report
from migration import export_report_csv, migrate_accounts, migrated_report

BASE_DIR = Path(__file__).resolve().parent
RECORDS_PATH = BASE_DIR / "data" / "legacy_accounts.json"
DICTIONARY_PATH = BASE_DIR / "data" / "dictionary.json"
DATABASE_PATH = BASE_DIR / "data" / "loan_fees.db"
EXPORT_PATH = BASE_DIR / "data" / "reconciliation.csv"

class LoanFeeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Legacy Loan Fee Review")
        self.account_id = tk.StringVar(value="LN-1001")
        self.report_text = tk.StringVar(value="Choose an action to inspect the workflow.")
        self.status_text = tk.StringVar(value="Ready")
        frame = ttk.Frame(root, padding=16)
        frame.grid()
        ttk.Label(frame, text="Account ID").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.account_id, width=18).grid(row=0, column=1, sticky="w")
        for column, (label, command) in enumerate([("Load Legacy", self.load_legacy), ("Migrate to SQLite", self.migrate), ("Load SQLite", self.load_sqlite), ("Export CSV", self.export_csv)]):
            ttk.Button(frame, text=label, command=command).grid(row=1, column=column, padx=4, pady=8)
        ttk.Label(frame, textvariable=self.report_text, justify="left").grid(row=2, column=0, columnspan=4, sticky="w")
        ttk.Label(frame, textvariable=self.status_text).grid(row=3, column=0, columnspan=4, sticky="w", pady=8)
    def selected_account(self): return self.account_id.get().strip()
    def show_report(self, report): self.report_text.set(format_report(report)); self.status_text.set("Report loaded")
    def show_error(self, error): self.status_text.set(f"Error: {error}")
    def load_legacy(self):
        try: self.show_report(legacy_report(self.selected_account(), RECORDS_PATH, DICTIONARY_PATH))
        except Exception as error: self.show_error(error)
    def migrate(self):
        try: migrate_accounts(RECORDS_PATH, DICTIONARY_PATH, DATABASE_PATH); self.status_text.set(f"Migration complete: {DATABASE_PATH.name}")
        except Exception as error: self.show_error(error)
    def load_sqlite(self):
        try: self.show_report(migrated_report(self.selected_account(), DATABASE_PATH))
        except Exception as error: self.show_error(error)
    def export_csv(self):
        try: export_report_csv(migrated_report(self.selected_account(), DATABASE_PATH), EXPORT_PATH); self.status_text.set(f"Export complete: {EXPORT_PATH.name}")
        except Exception as error: self.show_error(error)

if __name__ == "__main__":
    root = tk.Tk()
    LoanFeeApp(root)
    root.mainloop()
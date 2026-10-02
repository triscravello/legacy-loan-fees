import sqlite3
import tkinter as tk

root = tk.Tk()
root.title("Legacy Lab Ready")
message = f"Python GUI ready\nSQLite {sqlite3.sqlite_version} ready"
tk.Label(root, text=message).pack()
root.mainloop()

import csv
import sqlite3
from decimal import Decimal
from pathlib import Path

from legacy import associated_fees, extract_field, load_json

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    account_status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS account_fees (
    account_id TEXT NOT NULL,
    ordinal INTEGER NOT NULL CHECK (ordinal > 0),
    fee_code TEXT NOT NULL,
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0),
    PRIMARY KEY (account_id, ordinal),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);
"""


def amount_to_cents(amount):
    return int(amount * Decimal("100"))


def cents_to_amount(cents):
    return (Decimal(cents) / Decimal("100")).quantize(Decimal("0.01"))


def migrate_accounts(records_path, dictionary_path, database_path):
    records = load_json(records_path)
    dictionary = load_json(dictionary_path)
    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA)
        with connection:
            connection.execute("DELETE FROM account_fees")
            connection.execute("DELETE FROM accounts")
            for account_id, record in records.items():
                customer = extract_field(record, dictionary["CUSTOMER_NAME"]["position"])
                status = extract_field(record, dictionary["ACCOUNT_STATUS"]["position"])
                connection.execute("INSERT INTO accounts(account_id, customer_name, account_status) VALUES (?, ?, ?)", (account_id, customer, status))
                fee_rows = []
                for fee in associated_fees(record, dictionary):
                    fee_rows.append(
                        (
                            account_id,
                            fee["ordinal"],
                            fee["fee_code"],
                            amount_to_cents(fee["amount"]),
                        )
                    )

                connection.executemany(
                    """
                    INSERT INTO account_fees(
                        account_id, ordinal, fee_code, amount_cents
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    fee_rows,
                )
                
    finally:
        connection.close()


def migrated_report(account_id, database_path):
    connection = sqlite3.connect(database_path)
    try:
        result_rows = connection.execute("SELECT a.account_id, a.customer_name, a.account_status, f.ordinal, f.fee_code, f.amount_cents FROM accounts AS a LEFT JOIN account_fees AS f ON f.account_id = a.account_id WHERE a.account_id = ? ORDER BY f.ordinal", (account_id,)).fetchall()
    finally:
        connection.close()
    if not result_rows:
        raise KeyError(f"Unknown account: {account_id}")
    first = result_rows[0]
    fee_rows = [{"ordinal": row[3], "fee_code": row[4] or "[MISSING CODE]", "amount": cents_to_amount(row[5])} for row in result_rows if row[3] is not None]
    return {"source": "SQLite", "account_id": first[0], "customer": first[1], "status": first[2], "rows": fee_rows, "total": sum((row["amount"] for row in fee_rows), Decimal("0.00"))}


def export_report_csv(report, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.writer(target)
        writer.writerow(["account_id", "ordinal", "fee_code", "amount"])
        for row in report["rows"]:
            writer.writerow([report["account_id"], row["ordinal"], row["fee_code"], f"{row['amount']:.2f}"])
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

FIELD_MARK = chr(254)
VALUE_MARK = chr(253)
TWOPLACES = Decimal("0.01")


def load_json(path):
    with Path(path).open(encoding="utf-8") as source:
        return json.load(source)


def extract_field(record, field_number):
    fields = record.split(FIELD_MARK)
    offset = field_number - 1
    return fields[offset] if 0 <= offset < len(fields) else ""


def extract_values(record, field_number):
    field = extract_field(record, field_number)
    return field.split(VALUE_MARK) if field else []


def parse_amount(raw_amount):
    try:
        return Decimal(raw_amount or "0").quantize(TWOPLACES)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid fee amount: {raw_amount!r}") from exc


def associated_fees(record, dictionary):
    code_position = dictionary["FEE_CODES"]["position"]
    amount_position = dictionary["FEE_AMOUNTS"]["position"]
    codes = extract_values(record, code_position)
    amounts = extract_values(record, amount_position)
    fees = []
    for offset in range(max(len(codes), len(amounts))):
        fee_code = codes[offset].strip() if offset < len(codes) else ""
        raw_amount = amounts[offset].strip() if offset < len(amounts) else ""
        fees.append({"ordinal": offset + 1, "fee_code": fee_code, "amount": parse_amount(raw_amount)})
    return fees


def build_fee_report(account_id, records, dictionary, source_name):
    if account_id not in records:
        raise KeyError(f"Unknown account: {account_id}")
    record = records[account_id]
    customer = extract_field(record, dictionary["CUSTOMER_NAME"]["position"])
    status = extract_field(record, dictionary["ACCOUNT_STATUS"]["position"])
    rows = [{"ordinal": fee["ordinal"], "fee_code": fee["fee_code"] or "[MISSING CODE]", "amount": fee["amount"]} for fee in associated_fees(record, dictionary)]
    return {"source": source_name, "account_id": account_id, "customer": customer, "status": status, "rows": rows, "total": sum((row["amount"] for row in rows), Decimal("0.00"))}


def legacy_report(account_id, records_path, dictionary_path):
    return build_fee_report(account_id, load_json(records_path), load_json(dictionary_path), "Legacy dynamic array")


def format_report(report):
    lines = [f"Source: {report['source']}", f"Account: {report['account_id']}", f"Customer: {report['customer']}", f"Status: {report['status']}", "", "Pos | Fee code           | Amount", "----------------------------------"]
    for row in report["rows"]:
        lines.append(f"{row['ordinal']:>3} | {row['fee_code']:<18} | ${row['amount']:.2f}")
    lines.extend(["----------------------------------", f"Total: ${report['total']:.2f}"])
    return "\n".join(lines)
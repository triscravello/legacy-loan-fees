# Debug and Migrate a Legacy Loan Fee Workflow

## Incident summary

The legacy fee report independently removed blank fee codes before pairing codes with amounts. For account `LN-1001`, this shifted `LATE` from its third MultiValue position to the second amount, discarded the final amount, and produced `$150.00` instead of `$160.00`.

## Root cause and repair

The fee-code and fee-amount fields are associated by ordinal position. The repair iterates to the longer field length and reads both values at the same offset. A blank code is displayed as `[MISSING CODE]` so the data-quality issue remains visible.

## Storage migration

The legacy fixture stores one Field Mark-delimited record per account. Fee codes and amounts are Value Mark-delimited fields selected through dictionary metadata.

The SQLite design uses:

- `accounts` for one row per loan account
- `account_fees` for one row per fee occurrence
- `(account_id, ordinal)` as the fee identity
- integer cents for stored monetary values
- a foreign key from fee rows to their account

## OpenInsight concept mapping

| OpenInsight-oriented concept | Local implementation |
| --- | --- |
| Dynamic array record | Field Mark-delimited JSON string |
| Multivalued field | Value Mark-delimited field |
| Dictionary column | `data/dictionary.json` metadata |
| BASIC+ stored procedure | Procedural function in `legacy.py` or `migration.py` |
| Form event handler | Tkinter button callback |
| OpenList retrieval/report | Ordered parameterized SQLite query |
| Debugger inspection | Reproduction fixture plus `unittest` regression |

This is a conceptual maintenance lab, not an import-compatible OpenInsight dictionary or database export.

## Run the form

```text
python3.14 app.py
```

Use `LN-1001` to demonstrate the repaired incomplete association. Use `LN-1002` to demonstrate unchanged behavior for well-formed data.


## Run the tests

```text
python3.14 -m unittest -v
```

## Validation evidence

The automated checks prove that:

1. All three `LN-1001` fee positions survive the repair.
2. The corrected legacy and SQLite reports match.
3. The reconciliation CSV contains every migrated position.

## Migration trade-offs

SQLite was chosen over keeping JSON as the target because explicit parent-child rows, keys, constraints, ordered queries, and parameter binding make the migration decisions visible. Tkinter keeps the form event flow local and dependency-free while preserving the desktop maintenance feel.
<img src="https://cdn.prod.website-files.com/677c400686e724409a5a7409/6790ad949cf622dc8dcd9fe4_nextwork-logo-leather.svg" alt="NextWork" width="300" />

# Debug and Migrate a Legacy Loan Fee Workflow

**Project Link:** [View Project](https://nextwork.ai/projects/eb74c60f-40c3-4d71-a3ca-674ae4e1f956)

**Author:** Tristan Cravello  
**Email:** tlcravello@gmail.com

---

![Project overview](https://nextwork.ai/intense_teal_innocent_alligator/uploads/eb74c60f-40c3-4d71-a3ca-674ae4e1f956_4pa2o3a7)

## Project objective

This project recreates a deliberately fragile legacy loan-fee workflow, reproduces a positional MultiValue reporting defect, repairs the defect, migrates the corrected workflow to SQLite, and proves migration parity with automated tests and reconciliation evidence.

The goal is to demonstrate how to modernize a legacy data workflow without losing implicit sequence associations, blank historical positions, duplicate occurrences, or report totals.

## Incident summary

The legacy fee report independently removed blank fee codes before pairing codes with amounts.

For account `LN-1001`, this shifted `LATE` from its third MultiValue position to the second amount, discarded the final amount, and produced `$150.00` instead of the correct `$160.00`.

Migration-safety evidence includes:

- Passing parity tests
- Reconciliation output
- Regression coverage for the original defect
- Preservation of duplicate fee occurrences
- Incident-focused documentation

## Preparing the Local Legacy Maintenance Lab

### Setting up the project environment

The project uses a local, Git-tracked Python workspace with supporting data and test directories.

A verification script confirms that the runtime can load Tkinter and access the active SQLite build before the workflow is debugged or migrated.

![Environment setup](https://nextwork.ai/intense_teal_innocent_alligator/uploads/eb74c60f-40c3-4d71-a3ca-674ae4e1f956_4c31u2wu)

### Verifying Tkinter and SQLite support

Python is used for both the legacy-maintenance simulation and migration workflow.

Tkinter provides a lightweight desktop form, while SQLite provides a normalized relational target without adding external infrastructure.

## Reproducing the Misaligned Fee Report

### Creating the deliberate legacy failure

The legacy fixture stores one Field Mark-delimited record per account. Fee codes and fee amounts are Value Mark-delimited fields selected through dictionary metadata.

The deliberately naive report removes blank fee codes before pairing codes and amounts. That breaks the positional relationship between the two MultiValue fields.

![Legacy failure reproduction](https://nextwork.ai/intense_teal_innocent_alligator/uploads/eb74c60f-40c3-4d71-a3ca-674ae4e1f956_e4f0l8dq)

### Evidence of corrupted fee positions

For `LN-1001`, the naive path pairs `LATE` with `$25.00` and drops the final `$10.00` amount because the blank fee-code position is removed before `zip()` pairs the lists.

That produces the incorrect `$150.00` total.

## Root Cause and Repair

### Repairing positional MultiValue associations

The fee-code and fee-amount fields are associated by ordinal position, so the repair must preserve those positions even when one field contains a blank value.

The corrected logic iterates to the longer field length and reads both values at the same offset.

A blank code is displayed as `[MISSING CODE]` so the data-quality issue remains visible rather than being silently discarded.

![MultiValue repair](https://nextwork.ai/intense_teal_innocent_alligator/uploads/eb74c60f-40c3-4d71-a3ca-674ae4e1f956_3r0bam48)

### Why shared offsets fix the defect

A shared ordinal preserves alignment because both fee codes and fee amounts are retrieved from the same relative position.

Later values never shift forward simply because an earlier fee code is blank.

The regression test protects the corrected `$160.00` result for `LN-1001`.

## Migrating the Corrected Workflow to SQLite

### Normalized storage design

The SQLite design uses:

- `accounts` for one row per loan account
- `account_fees` for one row per fee occurrence
- `(account_id, ordinal)` as the fee identity
- integer cents for stored monetary values
- a foreign key from fee rows to their account

![SQLite migration](https://nextwork.ai/intense_teal_innocent_alligator/uploads/eb74c60f-40c3-4d71-a3ca-674ae4e1f956_1a460nad)

### Preserving fee identity with account and ordinal

The composite key `(account_id, ordinal)` preserves the sequence slot of every fee occurrence.

Queries can reconstruct the original ordering with:

```sql
ORDER BY ordinal
```

This is important because a fee code or monetary amount alone is not sufficient to identify an occurrence safely.

## Protecting Duplicate Fee Occurrences

![Duplicate fee protection](https://nextwork.ai/intense_teal_innocent_alligator/uploads/eb74c60f-40c3-4d71-a3ca-674ae4e1f956_49v5ogc1)

Duplicate fee codes must remain separate when they occur in different positions.

Treating the fee code itself as the unique identity could collapse valid repeated occurrences during migration.

Using ordinal position as part of the identity preserves duplicates and prevents a migration regression from silently reducing multiple fee rows into one.

## Proving Migration Parity and Reconciliation

### Validating corrected behavior across both workflows

The final workflow compares the corrected legacy parsing path with the SQLite-backed path to verify that both produce the same report output.

The reconciliation export also proves that every original positional fee entry survives migration.

### Isolating test state with temporary databases

Each test starts with a fresh temporary database in a disposable directory.

Cleanup automatically removes the temporary directory and its contents after each test, keeping tests independent and repeatable.

### Validation evidence

The automated checks prove that:

1. All three `LN-1001` fee positions survive the repair.
2. The corrected legacy and SQLite reports match.
3. The reconciliation CSV contains every migrated position.
4. The blank second fee-code position remains visible as `[MISSING CODE]`.
5. Duplicate fee occurrences remain distinct because ordinal position is preserved.

![Parity and reconciliation](https://nextwork.ai/intense_teal_innocent_alligator/uploads/eb74c60f-40c3-4d71-a3ca-674ae4e1f956_4pa2o3a7)

## OpenInsight Concept Mapping

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

## Run the Form

```text
python3.14 app.py
```

Use `LN-1001` to demonstrate the repaired incomplete association.

Use `LN-1002` to demonstrate unchanged behavior for well-formed data.

## Run the Tests

```text
python3.14 -m unittest -v
```

## Migration Trade-offs

SQLite was chosen over keeping JSON as the migration target because explicit parent-child rows, keys, constraints, ordered queries, and parameter binding make the migration decisions visible and testable.

Tkinter keeps the form event flow local and dependency-free while preserving the feel of desktop application maintenance.

The migration favors explicit relational structure over compact legacy encoding so that data identity, ordering, validation, and reconciliation can be inspected directly.

## Tools and Concepts Applied

The key tools used in this project include:

- Python 3.14
- Tkinter
- SQLite
- Python `unittest`
- `TemporaryDirectory`
- `addCleanup()`
- Git
- GitHub

Key concepts demonstrated include:

- Debugging positional MultiValue data
- Identifying data corruption caused by filtering before `zip()`
- Preserving blank positions with offset-aware iteration
- Normalizing legacy records into parent-child relational tables
- Using a composite primary key to preserve sequence identity
- Storing money as integer cents
- Writing regression and parity tests
- Reconciling legacy and migrated outputs
- Protecting duplicate occurrences during migration

## Project Reflection

This project took approximately one hour.

The most challenging parts were debugging Python test discovery and designing the repair so that uneven positional lists could be processed without losing alignment.

The test discovery issue was resolved by adding an empty `__init__.py` file so the `tests` directory was recognized as a package.

The project reinforced an important migration principle: correcting the schema is only part of the job. A safe migration also needs behavioral parity, explicit identity rules, regression tests, and reconciliation evidence.

A future extension would be to benchmark higher-throughput migration workloads, explore more advanced indexing strategies, or build evaluation harnesses for modern data and AI systems.

---

**Built with [NextWork](https://nextwork.ai)** — [View this project](https://nextwork.ai/projects/eb74c60f-40c3-4d71-a3ca-674ae4e1f956)
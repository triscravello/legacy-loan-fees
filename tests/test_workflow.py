import tempfile
import unittest
from pathlib import Path

from legacy import legacy_report
from migration import export_report_csv, migrate_accounts, migrated_report

BASE_DIR = Path(__file__).resolve().parents[1]
RECORDS_PATH = BASE_DIR / "data" / "legacy_accounts.json"
DICTIONARY_PATH = BASE_DIR / "data" / "dictionary.json"
DUPLICATE_PATH = BASE_DIR / "data" / "duplicate_fee_fixture.json"


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.database_path = Path(self.temp_directory.name) / "loan_fees.db"
        migrate_accounts(RECORDS_PATH, DICTIONARY_PATH, self.database_path)

    def test_legacy_association_preserves_blank_position(self):
        report = legacy_report("LN-1001", RECORDS_PATH, DICTIONARY_PATH)
        self.assertEqual(["ORIGINATION", "[MISSING CODE]", "LATE"], [row["fee_code"] for row in report["rows"]])
        self.assertEqual(["125.00", "25.00", "10.00"], [f"{row['amount']:.2f}" for row in report["rows"]])
        self.assertEqual("160.00", f"{report['total']:.2f}")

    
    def test_sqlite_report_matches_corrected_legacy(self):
        legacy = legacy_report("LN-1001", RECORDS_PATH, DICTIONARY_PATH)
        migrated = migrated_report("LN-1001", self.database_path)
        for key in ("account_id", "customer", "status", "rows", "total"):
            self.assertEqual(legacy[key], migrated[key])

    def test_csv_export_contains_all_positions(self):
        report = migrated_report("LN-1001", self.database_path)
        output_path = Path(self.temp_directory.name) / "reconciliation.csv"
        export_report_csv(report, output_path)
        content = output_path.read_text(encoding="utf-8")
        self.assertIn("LN-1001,1,ORIGINATION,125.00", content)
        self.assertIn("LN-1001,2,[MISSING CODE],25.00", content)
        self.assertIn("LN-1001,3,LATE,10.00", content)

    def test_duplicate_fee_codes_are_not_collapsed(self):
        migrate_accounts(DUPLICATE_PATH, DICTIONARY_PATH, self.database_path)
        report = migrated_report("LN-2001", self.database_path)
        self.assertEqual(["LATE", "LATE"], [row["fee_code"] for row in report["rows"]])
        self.assertEqual(
            ["5.00", "7.50"],
            [f"{row['amount']:.2f}" for row in report["rows"]],
        )


if __name__ == "__main__":
    unittest.main()
"""
Tests for CSV export module
"""

import tempfile
import csv
from pathlib import Path
from src.csv_export import CSVExporter
from src.scraper import Giveaway


def test_export_giveaways():
    """Test exporting giveaways to CSV"""
    giveaways = [
        Giveaway("Test 1", "https://gleam.io/test1", "Description 1"),
        Giveaway("Test 2", "https://gleam.io/test2", "Description 2"),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"
        success = CSVExporter.export(giveaways, str(csv_path))

        assert success
        assert csv_path.exists()

        # Verify CSV contents
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["Title"] == "Test 1"
        assert rows[0]["URL"] == "https://gleam.io/test1"
        assert rows[1]["Title"] == "Test 2"


def test_export_empty_list():
    """Test exporting empty giveaway list"""
    giveaways = []

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "empty.csv"
        success = CSVExporter.export(giveaways, str(csv_path))

        assert success
        assert csv_path.exists()

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 0


def test_export_with_empty_description():
    """Test exporting giveaway with no description"""
    giveaways = [Giveaway("Test", "https://gleam.io/test")]

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"
        CSVExporter.export(giveaways, str(csv_path))

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert rows[0]["Description"] == ""


def test_filename_suggestion():
    """Test filename suggestion generation"""
    filename = CSVExporter.get_filename_suggestion()
    assert filename.startswith("giveaways_")
    assert filename.endswith(".csv")

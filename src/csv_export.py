"""
CSV export functionality for giveaways
"""

import csv
import logging
from pathlib import Path
from typing import List

from .scraper import Giveaway

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVExporter:
    """Handles exporting giveaways to CSV format"""

    @staticmethod
    def export(giveaways: List[Giveaway], filepath: str) -> bool:
        """Export giveaways to CSV file

        Args:
            giveaways: List of Giveaway objects to export
            filepath: Path to output CSV file

        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Title", "URL", "Description"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for giveaway in giveaways:
                    writer.writerow(
                        {
                            "Title": giveaway.title,
                            "URL": giveaway.url,
                            "Description": giveaway.description or "",
                        }
                    )

            logger.info(
                f"Successfully exported {len(giveaways)} giveaways to {filepath}"
            )
            return True

        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False

    @staticmethod
    def get_filename_suggestion() -> str:
        """Get a suggested filename with timestamp"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"giveaways_{timestamp}.csv"

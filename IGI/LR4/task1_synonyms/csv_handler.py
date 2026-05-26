"""
csv_handler.py — CSV serialisation for SynonymDictionary (Task 1, Variant 11).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11
"""

import csv
import os
from task1_synonyms.models import SynonymDictionary


# ─────────────────────────────────────────────
#  CSV HANDLER CLASS
# ─────────────────────────────────────────────

class CSVHandler:
    """
    Handles saving and loading a SynonymDictionary to/from a CSV file.

    Demonstrates:
      - Static attributes (FIELDNAMES, DEFAULT_PATH)
      - Static methods (validate_path)
      - Instance methods for read/write
    """

    FIELDNAMES: list  = ["word1", "word2"]          # static attribute
    DEFAULT_PATH: str = "data/synonyms.csv"          # static attribute

    def __init__(self, filepath: str = ""):
        """
        Initialize the handler with an optional custom file path.

        Args:
            filepath (str): Path to the CSV file. Uses DEFAULT_PATH if empty.
        """
        self._filepath: str = filepath or self.DEFAULT_PATH   # dynamic attribute

    # ── property ───────────────────────────────────────

    @property
    def filepath(self) -> str:
        """Path to the CSV file."""
        return self._filepath

    @filepath.setter
    def filepath(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("File path cannot be empty.")
        self._filepath = value.strip()

    # ── static helpers ─────────────────────────────────

    @staticmethod
    def validate_path(path: str) -> bool:
        """
        Check that the path's parent directory exists.

        Args:
            path (str): File path to validate.

        Returns:
            bool: True if the directory exists.
        """
        parent = os.path.dirname(path) or "."
        return os.path.isdir(parent)

    # ── write ──────────────────────────────────────────

    def save(self, dictionary: SynonymDictionary) -> None:
        """
        Save a SynonymDictionary to the CSV file.

        Args:
            dictionary (SynonymDictionary): The dictionary to save.

        Raises:
            OSError: If the file cannot be written.
        """
        os.makedirs(os.path.dirname(self._filepath) or ".", exist_ok=True)
        with open(self._filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writeheader()
            for pair in dictionary.pairs:
                writer.writerow(pair.as_dict())
        print(f"  [CSV] Сохранено {len(dictionary.pairs)} пар → {self._filepath}")

    # ── read ───────────────────────────────────────────

    def load(self, dictionary: SynonymDictionary) -> None:
        """
        Load pairs from a CSV file into an existing SynonymDictionary.

        Args:
            dictionary (SynonymDictionary): Target dictionary to populate.

        Raises:
            FileNotFoundError: If the CSV file does not exist.
            ValueError:        If a row has invalid/missing fields.
        """
        if not os.path.exists(self._filepath):
            raise FileNotFoundError(f"CSV file not found: {self._filepath}")

        with open(self._filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count  = 0
            for row in reader:
                w1 = row.get("word1", "").strip()
                w2 = row.get("word2", "").strip()
                if not w1 or not w2:
                    raise ValueError(f"Invalid row in CSV: {row}")
                dictionary.add_pair(w1, w2)
                count += 1
        print(f"  [CSV] Загружено {count} пар ← {self._filepath}")

    def __repr__(self) -> str:
        return f"CSVHandler(filepath={self._filepath!r})"

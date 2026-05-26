"""
pickle_handler.py — Pickle serialisation for SynonymDictionary (Task 1, Variant 11).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11
"""

import pickle
import os
from task1_synonyms.models import SynonymDictionary


# ─────────────────────────────────────────────
#  PICKLE HANDLER CLASS
# ─────────────────────────────────────────────

class PickleHandler:
    """
    Handles saving and loading a SynonymDictionary to/from a binary pickle file.

    Unlike CSVHandler, pickle serialises the entire object graph in one call,
    preserving the full SynonymDictionary state (including name and history).
    """

    DEFAULT_PATH: str = "data/synonyms.pkl"     # static attribute

    def __init__(self, filepath: str = ""):
        """
        Initialize the handler with an optional custom file path.

        Args:
            filepath (str): Path to the pickle file. Uses DEFAULT_PATH if empty.
        """
        self._filepath: str = filepath or self.DEFAULT_PATH   # dynamic attribute

    # ── property ───────────────────────────────────────

    @property
    def filepath(self) -> str:
        """Path to the pickle file."""
        return self._filepath

    @filepath.setter
    def filepath(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Filepath cannot be empty.")
        self._filepath = value.strip()

    # ── write ──────────────────────────────────────────

    def save(self, dictionary: SynonymDictionary) -> None:
        """
        Serialise and save the entire SynonymDictionary object to a .pkl file.

        Args:
            dictionary (SynonymDictionary): The object to pickle.

        Raises:
            OSError: If the file cannot be written.
        """
        os.makedirs(os.path.dirname(self._filepath) or ".", exist_ok=True)
        with open(self._filepath, "wb") as f:
            pickle.dump(dictionary, f, protocol=pickle.HIGHEST_PROTOCOL)
        size = os.path.getsize(self._filepath)
        print(f"  [Pickle] Сохранено → {self._filepath}  ({size} байт)")

    # ── read ───────────────────────────────────────────

    def load(self) -> SynonymDictionary:
        """
        Deserialise a SynonymDictionary from a .pkl file.

        Returns:
            SynonymDictionary: The restored object.

        Raises:
            FileNotFoundError: If the pickle file does not exist.
            pickle.UnpicklingError: If the file is corrupted or incompatible.
        """
        if not os.path.exists(self._filepath):
            raise FileNotFoundError(f"Pickle file not found: {self._filepath}")

        with open(self._filepath, "rb") as f:
            obj = pickle.load(f)

        if not isinstance(obj, SynonymDictionary):
            raise TypeError(f"Expected SynonymDictionary, got {type(obj).__name__}")

        print(f"  [Pickle] Загружено ← {self._filepath}  ({len(obj)} записей)")
        return obj

    def __repr__(self) -> str:
        return f"PickleHandler(filepath={self._filepath!r})"

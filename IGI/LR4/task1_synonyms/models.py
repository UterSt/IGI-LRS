"""
models.py — OOP models for the Synonym Dictionary (Task 1, Variant 11).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Demonstrates:
  - Static and dynamic class attributes
  - Polymorphism  (find_synonym overridden in subclass)
  - Magic methods (__str__, __repr__, __len__, __contains__, __iter__, __getitem__)
  - super()
  - Getters and setters (@property)
  - Class properties (@classmethod)
  - Mixins (LogMixin, ValidationMixin)
"""


# ─────────────────────────────────────────────
#  MIXINS
# ─────────────────────────────────────────────

class LogMixin:
    """Mixin that adds optional console logging to any class."""

    _log_enabled: bool = True           # static (class-level) attribute

    def log(self, message: str) -> None:
        """
        Print a log message if logging is enabled.

        Args:
            message (str): The message to log.
        """
        if self.__class__._log_enabled:
            print(f"  [ЛОГ] {message}")

    @classmethod
    def set_logging(cls, enabled: bool) -> None:
        """
        Enable or disable logging for this class.

        Args:
            enabled (bool): True to enable, False to disable.
        """
        cls._log_enabled = enabled


class ValidationMixin:
    """Mixin that provides common validation helpers."""

    @staticmethod
    def validate_word(word) -> bool:
        """
        Check that a word is a non-empty string.

        Args:
            word: Value to validate.

        Returns:
            bool: True if valid.
        """
        return isinstance(word, str) and bool(word.strip())


# ─────────────────────────────────────────────
#  BASE COLLECTION
# ─────────────────────────────────────────────

class BaseCollection(ValidationMixin):
    """
    Abstract-ish base class for keyed collections.

    Demonstrates static attribute (_instance_count) and magic methods.
    """

    _instance_count: int = 0            # static attribute — shared across instances

    def __init__(self):
        BaseCollection._instance_count += 1
        self._data: dict = {}           # dynamic attribute — unique to each instance

    # ── magic methods ──────────────────────────────────

    def __len__(self) -> int:
        """Return the number of entries stored."""
        return len(self._data)

    def __contains__(self, item) -> bool:
        """Support the 'in' operator."""
        return item in self._data

    def __iter__(self):
        """Allow iteration over keys."""
        return iter(self._data)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(entries={len(self._data)})"

    # ── class method ───────────────────────────────────

    @classmethod
    def get_instance_count(cls) -> int:
        """
        Return how many instances of BaseCollection (and subclasses) exist.

        Returns:
            int: Total instance count.
        """
        return cls._instance_count


# ─────────────────────────────────────────────
#  SYNONYM PAIR
# ─────────────────────────────────────────────

class SynonymPair:
    """
    Represents a single synonym pair (word1 <-> word2).

    Demonstrates getters/setters via @property.
    """

    def __init__(self, word1: str, word2: str):
        """
        Initialize a SynonymPair with two words.

        Args:
            word1 (str): First word.
            word2 (str): Second word (its synonym).

        Raises:
            ValueError: If either word is not a non-empty string.
        """
        self._word1: str = ""           # dynamic attribute
        self._word2: str = ""
        self.word1 = word1              # goes through setter
        self.word2 = word2

    # ── properties (getters + setters) ─────────────────

    @property
    def word1(self) -> str:
        """First word of the pair."""
        return self._word1

    @word1.setter
    def word1(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"word1 must be a non-empty string, got: {value!r}")
        self._word1 = value.strip().lower()

    @property
    def word2(self) -> str:
        """Second word of the pair."""
        return self._word2

    @word2.setter
    def word2(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"word2 must be a non-empty string, got: {value!r}")
        self._word2 = value.strip().lower()

    # ── magic methods ──────────────────────────────────

    def __str__(self) -> str:
        return f"{self._word1!r:20s} <->  {self._word2!r}"

    def __repr__(self) -> str:
        return f"SynonymPair({self._word1!r}, {self._word2!r})"

    def __eq__(self, other) -> bool:
        """Two pairs are equal if they contain the same words (in any order)."""
        if not isinstance(other, SynonymPair):
            return NotImplemented
        return ({self._word1, self._word2} == {other._word1, other._word2})

    def __hash__(self) -> int:
        return hash(frozenset([self._word1, self._word2]))

    def as_dict(self) -> dict:
        """
        Return the pair as a plain dict (useful for serialisation).

        Returns:
            dict: {'word1': ..., 'word2': ...}
        """
        return {"word1": self._word1, "word2": self._word2}


# ─────────────────────────────────────────────
#  SYNONYM DICTIONARY  (base)
# ─────────────────────────────────────────────

class SynonymDictionary(BaseCollection, LogMixin):
    """
    Dictionary of synonym pairs with search, insert, and display.

    Inherits from BaseCollection (collection logic) and LogMixin (logging).
    Uses super() to chain __init__ calls.
    """

    _default_name: str = "Synonym Dictionary"  # static attribute

    def __init__(self, name: str = ""):
        super().__init__()                      # calls BaseCollection.__init__
        self._name: str = name or self._default_name   # dynamic attribute
        self._pairs: list[SynonymPair] = []
        self.log(f"Created: {self._name}")

    # ── property ───────────────────────────────────────

    @property
    def name(self) -> str:
        """Human-readable name of this dictionary."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Dictionary name cannot be empty.")
        self._name = value.strip()

    @property
    def pairs(self) -> list:
        """Read-only copy of all SynonymPair objects."""
        return list(self._pairs)

    # ── mutation ───────────────────────────────────────

    def add_pair(self, word1: str, word2: str) -> None:
        """
        Add a synonym pair to the dictionary.

        Args:
            word1 (str): First word.
            word2 (str): Second word.

        Raises:
            ValueError: If either word is invalid.
        """
        pair = SynonymPair(word1, word2)        # setter validates
        self._pairs.append(pair)
        self._data[pair.word1] = pair.word2
        self._data[pair.word2] = pair.word1
        self.log(f"Added: {pair}")

    # ── search ─────────────────────────────────────────

    def find_synonym(self, word: str):
        """
        Return the synonym for the given word, or None if not found.

        Args:
            word (str): Word to look up.

        Returns:
            str | None: The synonym, or None.
        """
        return self._data.get(word.strip().lower())

    def last_word_synonym(self) -> tuple:
        """
        Find the last word in the last pair and its synonym.

        Returns:
            tuple: (last_word, synonym) or (None, None) if empty.
        """
        if not self._pairs:
            return None, None
        last = self._pairs[-1].word2         # "last" word in last pair
        return last, self.find_synonym(last)

    # ── magic methods ──────────────────────────────────

    def __getitem__(self, word: str) -> str:
        """
        Allow dict-like access: dictionary['happy'].

        Raises:
            KeyError: If the word is not in the dictionary.
        """
        result = self.find_synonym(word)
        if result is None:
            raise KeyError(f"Word '{word}' not found in the dictionary.")
        return result

    def __str__(self) -> str:
        header = f"=== {self._name} ({len(self._pairs)} pairs) ===\n"
        rows   = "\n".join(f"  {p}" for p in self._pairs)
        return header + (rows if rows else "  (empty)")

    def __repr__(self) -> str:
        return f"SynonymDictionary(name={self._name!r}, pairs={len(self._pairs)})"


# ─────────────────────────────────────────────
#  EXTENDED DICTIONARY (polymorphism demo)
# ─────────────────────────────────────────────

class ExtendedSynonymDictionary(SynonymDictionary):
    """
    Extended version of SynonymDictionary that also tracks search history.

    Demonstrates polymorphism: find_synonym() overridden with super() call.
    """

    def __init__(self, name: str = "Extended Synonym Dictionary"):
        super().__init__(name)                  # super() to parent
        self._search_history: list[str] = []   # dynamic attribute

    def find_synonym(self, word: str):
        """
        Find synonym and log the search in history (polymorphic override).

        Args:
            word (str): Word to look up.

        Returns:
            str | None: The synonym, or None.
        """
        self._search_history.append(word.strip().lower())
        return super().find_synonym(word)       # delegate to parent

    @property
    def search_history(self) -> list:
        """Read-only copy of past searches."""
        return list(self._search_history)

    def clear_history(self) -> None:
        """Clear the search history."""
        self._search_history.clear()
        self.log("Search history cleared.")

    def __repr__(self) -> str:
        return (f"ExtendedSynonymDictionary(name={self._name!r}, "
                f"pairs={len(self._pairs)}, searches={len(self._search_history)})")

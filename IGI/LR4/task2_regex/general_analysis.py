"""
general_analysis.py — Common text analysis functions for Task 2.
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

General requirements (all variants):
  - count total sentences and by type (declarative / interrogative / imperative)
  - average sentence length in characters (words only)
  - average word length
  - count smileys

Smiley definition:
  [;:] exactly once, then [-]* zero or more times,
  then one or more identical brackets from { ( ) [ ] }
"""

import re
from dataclasses import dataclass, field


# ─────────────────────────────────────────────
#  DATA CONTAINERS
# ─────────────────────────────────────────────

@dataclass
class SentenceStats:
    """Stores sentence-level statistics."""
    total:         int = 0
    declarative:   int = 0    # ends with '.'
    interrogative: int = 0    # ends with '?'
    imperative:    int = 0    # ends with '!'


@dataclass
class TextStats:
    """Aggregated statistics for a whole text."""
    sentences:     SentenceStats = field(default_factory=SentenceStats)
    avg_sent_len:  float = 0.0    # average sentence length (chars, words only)
    avg_word_len:  float = 0.0    # average word length in chars
    smiley_count:  int   = 0


# ─────────────────────────────────────────────
#  BASE ANALYSIS CLASS
# ─────────────────────────────────────────────

class TextAnalyzer:
    """
    Base class for text analysis.

    Demonstrates:
      - Static attributes (SMILEY_PATTERN, WORD_PATTERN)
      - Dynamic attributes (_text, _stats)
      - Properties with getters
      - Magic methods (__str__, __repr__, __len__)
    """

    #Regax all
    # static attributes — compiled once, shared by all instances
    WORD_PATTERN:   re.Pattern = re.compile(r"[A-Za-z']+")
    SENT_PATTERN:   re.Pattern = re.compile(r"[^.!?]+[.!?]", re.DOTALL)
    SMILEY_PATTERN: re.Pattern = re.compile(r"[;:][-]*(?:\(+|\)+|\[+|\]+)")

    def __init__(self, text: str):
        """
        Initialise the analyser with source text.

        Args:
            text (str): The text to analyse.

        Raises:
            ValueError: If text is empty.
        """
        if not text or not text.strip():
            raise ValueError("Text must not be empty.")
        self._text:  str       = text        # dynamic attribute
        self._stats: TextStats = TextStats() # dynamic attribute — computed lazily

    # ── properties ─────────────────────────────────────

    @property
    def text(self) -> str:
        """The raw source text."""
        return self._text

    @property
    def stats(self) -> TextStats:
        """Computed text statistics (triggers analysis on first access)."""
        return self._stats

    # ── magic methods ──────────────────────────────────

    def __len__(self) -> int:
        """Return the number of characters in the text."""
        return len(self._text)

    def __str__(self) -> str:
        s = self._stats
        return (
            f"TextAnalyzer | chars={len(self)} | "
            f"sentences={s.sentences.total} | "
            f"smileys={s.smiley_count}"
        )

    def __repr__(self) -> str:
        return f"TextAnalyzer(chars={len(self._text)})"

    # ── analysis methods ───────────────────────────────

    def _extract_words(self) -> list[str]:
        """
        Extract all words (letters only) from the text.

        Returns:
            list[str]: All words found.
        """
        return self.WORD_PATTERN.findall(self._text)

    def count_sentences(self) -> SentenceStats:
        """
        Count total sentences and classify each by terminal punctuation.

        Returns:
            SentenceStats: Counts for total, declarative, interrogative, imperative.
        """
        raw_sents = self.SENT_PATTERN.findall(self._text)
        stats = SentenceStats()
        stats.total = len(raw_sents)
        for s in raw_sents:
            stripped = s.strip()
            if stripped.endswith("."):
                stats.declarative   += 1
            elif stripped.endswith("?"):
                stats.interrogative += 1
            elif stripped.endswith("!"):
                stats.imperative    += 1
        return stats

    def avg_sentence_length(self) -> float:
        """
        Compute average sentence length in characters (counting only word chars).

        Returns:
            float: Average character count per sentence; 0.0 if no sentences.
        """
        sentences = self.SENT_PATTERN.findall(self._text)
        if not sentences:
            return 0.0
        word_chars_per_sentence = [
            sum(len(w) for w in self.WORD_PATTERN.findall(s))
            for s in sentences
        ]
        return sum(word_chars_per_sentence) / len(sentences)

    def avg_word_length(self) -> float:
        """
        Compute the average word length across the whole text.

        Returns:
            float: Average word length in characters; 0.0 if no words.
        """
        words = self._extract_words()
        if not words:
            return 0.0
        return sum(len(w) for w in words) / len(words)

    def count_smileys(self) -> int:
        """
        Count smileys in the text.

        Smiley = [;:] then [-]* then one or more same-type brackets.

        Returns:
            int: Number of smileys found.
        """
        return len(self.SMILEY_PATTERN.findall(self._text))

    def run_general_analysis(self) -> TextStats:
        """
        Run all general analyses and populate self._stats.

        Returns:
            TextStats: Filled statistics object.
        """
        self._stats.sentences    = self.count_sentences()
        self._stats.avg_sent_len = round(self.avg_sentence_length(), 2)
        self._stats.avg_word_len = round(self.avg_word_length(), 2)
        self._stats.smiley_count = self.count_smileys()
        return self._stats

    def print_general_stats(self) -> None:
        """Pretty-print the general analysis results."""
        s = self._stats
        print("\n  ── Общая статистика текста ──")
        print(f"  Всего предложений        : {s.sentences.total}")
        print(f"    Повествовательных (.)  : {s.sentences.declarative}")
        print(f"    Вопросительных    (?)  : {s.sentences.interrogative}")
        print(f"    Побудительных     (!)  : {s.sentences.imperative}")
        print(f"  Средняя длина предложения: {s.avg_sent_len} симв. (только слова)")
        print(f"  Средняя длина слова      : {s.avg_word_len} симв.")
        print(f"  Найдено смайликов        : {s.smiley_count}")
        smileys = self.SMILEY_PATTERN.findall(self._text)
        if smileys:
            print(f"  Список смайликов         : {smileys}")

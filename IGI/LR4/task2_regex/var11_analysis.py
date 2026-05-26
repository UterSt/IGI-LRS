"""
var11_analysis.py — Variant 11 specific text analysis using regular expressions.
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Variant 11 tasks:
  1. Print words containing chars in range 'a'..'o'  AND  at least one digit.
  2. Check whether a given string is a valid 6-digit decimal number
     (no leading zeros, digits 100000–999999).
  3. Count words enclosed in double quotes.
  4. Determine how many times each letter appears.
  5. Print all comma-separated phrases in alphabetical order.
"""

import re
from collections import Counter
from task2_regex.general_analysis import TextAnalyzer


# ─────────────────────────────────────────────
#  VARIANT 11 ANALYSER  (inherits TextAnalyzer)
# ─────────────────────────────────────────────

class Variant11Analyzer(TextAnalyzer):
    """
    Text analyser with Variant 11 specific analyses.

    Extends TextAnalyzer (polymorphism via method override of __str__).
    Demonstrates mixin-style extra attributes and all OOP requirements.
    """

    #Regax
    # static patterns — compiled once
    _WORD_WITH_AO_AND_DIGIT = re.compile(
        r"\b(?=[a-zA-Z0-9]*[0-9])(?=[a-zA-Z0-9]*[a-oA-O])[a-zA-Z0-9]+\b"
    )
    _SIX_DIGIT_NUMBER = re.compile(r"^[1-9]\d{5}$")
    _QUOTED_WORD      = re.compile(r'"([^"]+)"')
    _LETTER_ONLY      = re.compile(r"[A-Za-z]")
    _COMMA_PHRASE     = re.compile(r"[^,!?.]+")

    def __init__(self, text: str):
        """
        Initialise Variant11Analyzer.

        Args:
            text (str): Source text to analyse.
        """
        super().__init__(text)              # super() to TextAnalyzer
        self._v11_results: dict = {}        # dynamic attribute for cached results

    # ── property ───────────────────────────────────────

    @property
    def v11_results(self) -> dict:
        """Read-only cached results of variant-11 analyses."""
        return dict(self._v11_results)

    # ── polymorphic override ────────────────────────────

    def __str__(self) -> str:
        """Extend parent's __str__ with variant info."""
        base = super().__str__()
        return base + f" | variant=11"

    # ─────────────────────────────────────────────────
    #  VARIANT SPECIFIC ANALYSES
    # ─────────────────────────────────────────────────

    def words_with_ao_and_digit(self) -> list[str]:
        """
        Find all words that contain at least one letter in [a..o] OR [A..O]
        AND at least one digit.

        Returns:
            list[str]: Matching words (unique, sorted).
        """
        matches = self._WORD_WITH_AO_AND_DIGIT.findall(self._text)
        # Extra filter: must contain a letter in a-o range AND a digit
        result = []
        for w in matches:
            has_ao    = bool(re.search(r"[a-oA-O]", w))
            has_digit = bool(re.search(r"\d",       w))
            if has_ao and has_digit:
                result.append(w)
        return sorted(set(result))

    def check_six_digit_number(self, s: str) -> bool:
        """
        Check whether string s is a valid 6-digit decimal integer
        with no leading zeros (range 100000–999999).

        Args:
            s (str): String to validate.

        Returns:
            bool: True if valid.
        """
        return bool(self._SIX_DIGIT_NUMBER.match(s.strip()))

    def count_quoted_words(self) -> tuple[int, list[str]]:
        """
        Find all phrases enclosed in double quotes.

        Returns:
            tuple: (count, list_of_quoted_phrases)
        """
        found = self._QUOTED_WORD.findall(self._text)
        return len(found), found

    def letter_frequency(self) -> dict[str, int]:
        """
        Count how many times each letter appears (case-insensitive).

        Returns:
            dict[str, int]: Letter → count, sorted alphabetically.
        """
        letters = self._LETTER_ONLY.findall(self._text.lower())
        counts  = Counter(letters)
        return dict(sorted(counts.items()))

    def comma_phrases_alphabetical(self) -> list[str]:
        """
        Extract all comma-separated phrases and return them in alphabetical order.

        Returns:
            list[str]: Stripped phrases sorted alphabetically.
        """
        raw = self._COMMA_PHRASE.findall(self._text)
        phrases = [p.strip(" \n\r\t.!?") for p in raw if p.strip()]
        return sorted(phrases, key=str.lower)

    # ── run all variant analyses ────────────────────────

    def run_variant_analysis(self) -> dict:
        """
        Execute all Variant 11 specific analyses and cache results.

        Returns:
            dict: Results keyed by analysis name.
        """
        ao_words  = self.words_with_ao_and_digit()
        q_count, q_list = self.count_quoted_words()
        freq      = self.letter_frequency()
        phrases   = self.comma_phrases_alphabetical()

        self._v11_results = {
            "ao_digit_words":   ao_words,
            "quoted_count":     q_count,
            "quoted_phrases":   q_list,
            "letter_frequency": freq,
            "comma_phrases":    phrases,
        }
        return self._v11_results

    def print_variant_results(self) -> None:
        """Pretty-print all Variant 11 analysis results."""
        r = self._v11_results
        if not r:
            print("  [!] Сначала вызовите run_variant_analysis().")
            return

        print("\n  ── Вариант 11: Слова с символами [a-o] И цифрой ──")
        words = r["ao_digit_words"]
        if words:
            for w in words:
                print(f"    {w}")
        else:
            print("    (не найдено)")

        print("\n  ── Вариант 11: Слова в двойных кавычках ──")
        print(f"  Количество: {r['quoted_count']}")
        for q in r["quoted_phrases"]:
            print(f"    \"{q}\"")

        print("\n  ── Вариант 11: Частота букв ──")
        freq = r["letter_frequency"]
        items = list(freq.items())
        for i in range(0, len(items), 6):
            row = items[i:i+6]
            print("  " + "  ".join(f"{ch}:{cnt:>3}" for ch, cnt in row))

        print("\n  ── Вариант 11: Словосочетания через запятую (по алфавиту) ──")
        for i, p in enumerate(r["comma_phrases"], 1):
            print(f"  {i:>3}. {p}")

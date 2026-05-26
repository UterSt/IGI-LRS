"""
task1_main.py — Entry point for Task 1: Synonym Dictionary (Variant 11).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Task: Implement a synonym dictionary where every word is a synonym of its pair.
      Find the synonym of the last word; search by keyboard input.
      Two serialisation formats: CSV and pickle.
"""

import os
import sys

from utils import print_separator, input_string_nonempty, run_with_repeat
from task1_synonyms.models      import ExtendedSynonymDictionary
from task1_synonyms.csv_handler  import CSVHandler
from task1_synonyms.pickle_handler import PickleHandler


# ─────────────────────────────────────────────
#  SAMPLE DATA
# ─────────────────────────────────────────────

SAMPLE_PAIRS = [
    ("happy",    "joyful"),
    ("sad",      "unhappy"),
    ("big",      "large"),
    ("fast",     "quick"),
    ("smart",    "intelligent"),
    ("brave",    "courageous"),
    ("cold",     "chilly"),
    ("begin",    "start"),
    ("end",      "finish"),
    ("beautiful","gorgeous"),
]


def build_sample_dictionary() -> ExtendedSynonymDictionary:
    """
    Create and populate the sample synonym dictionary.

    Returns:
        ExtendedSynonymDictionary: Populated dictionary instance.
    """
    d = ExtendedSynonymDictionary("English Synonym Dictionary")
    d.set_logging(False)           # suppress pair-level logs for cleanliness
    for w1, w2 in SAMPLE_PAIRS:
        d.add_pair(w1, w2)
    d.set_logging(True)
    return d


# ─────────────────────────────────────────────
#  DISPLAY
# ─────────────────────────────────────────────

def display_dictionary(d: ExtendedSynonymDictionary) -> None:
    """
    Print the full contents of the synonym dictionary.

    Args:
        d (ExtendedSynonymDictionary): Dictionary to display.
    """
    print(d)                       # uses __str__ magic method


def display_last_word_synonym(d: ExtendedSynonymDictionary) -> None:
    """
    Find and display the synonym of the last word in the dictionary.

    Args:
        d (ExtendedSynonymDictionary): Dictionary to query.
    """
    last_word, synonym = d.last_word_synonym()
    if last_word is None:
        print("  Словарь пуст.")
        return
    print(f"\n  Последнее слово : '{last_word}'")
    print(f"  Его синоним     : '{synonym}'")


# ─────────────────────────────────────────────
#  SEARCH
# ─────────────────────────────────────────────

def search_by_word(d: ExtendedSynonymDictionary) -> None:
    """
    Prompt the user for a word and display its synonym.

    Args:
        d (ExtendedSynonymDictionary): Dictionary to search in.
    """
    word = input_string_nonempty("  Введите слово для поиска: ")
    result = d.find_synonym(word)     # polymorphic — logs to history in Extended version
    if result:
        print(f"  Синоним слова '{word}': '{result}'")
    else:
        print(f"  Слово '{word}' не найдено в словаре.")

    # Show search history (feature of ExtendedSynonymDictionary)
    print(f"  История поиска: {d.search_history}")


# ─────────────────────────────────────────────
#  CSV  FLOW
# ─────────────────────────────────────────────

def demo_csv(d: ExtendedSynonymDictionary) -> None:
    """
    Save the dictionary to CSV, then reload and verify.

    Args:
        d (ExtendedSynonymDictionary): Source dictionary.
    """
    handler = CSVHandler("data/synonyms.csv")
    handler.save(d)

    # Reload into a fresh dictionary
    fresh = ExtendedSynonymDictionary("Loaded from CSV")
    fresh.set_logging(False)
    handler.load(fresh)
    fresh.set_logging(True)

    print(f"\n  Перезагруженный словарь содержит {len(fresh)} записей.")
    print(f"  'happy' → '{fresh['happy']}'")    # __getitem__ magic method


# ─────────────────────────────────────────────
#  PICKLE FLOW
# ─────────────────────────────────────────────

def demo_pickle(d: ExtendedSynonymDictionary) -> None:
    """
    Save the entire dictionary object to pickle, then reload it.

    Args:
        d (ExtendedSynonymDictionary): Source dictionary.
    """
    handler = PickleHandler("data/synonyms.pkl")
    handler.save(d)

    restored = handler.load()
    print(f"  Восстановленное имя    : '{restored.name}'")
    print(f"  Восстановленных записей: {len(restored)}")
    print(f"  'fast'  → '{restored['fast']}'")   # __getitem__


# ─────────────────────────────────────────────
#  MAIN TASK ENTRY POINT
# ─────────────────────────────────────────────

def run_task1() -> None:
    """
    Main entry point for Task 1 — Synonym Dictionary.

    Builds the dictionary, demonstrates CSV and pickle serialisation,
    finds the last-word synonym, and allows keyboard-based search.
    """
    print_separator("Задание 1 — Словарь синонимов (Вариант 11)")

    d = build_sample_dictionary()

    print("\n  Полный словарь:")
    display_dictionary(d)

    print("\n  ── Синоним последнего слова ──")
    display_last_word_synonym(d)

    print(f"\n  repr(d) → {repr(d)}")
    print(f"  len(d)  → {len(d)} записей")
    print(f"  'smart' in d → {'smart' in d}")
    print(f"  Количество созданных экземпляров BaseCollection: "
          f"{d.get_instance_count()}")

    print("\n  ── Сериализация CSV ──")
    demo_csv(d)

    print("\n  ── Сериализация Pickle ──")
    demo_pickle(d)

    print("\n  ── Поиск по слову ──")
    search_by_word(d)

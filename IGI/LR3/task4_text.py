# =============================================================================
# Lab Work #3: Standard Data Types, Collections, Functions, Modules
# File: task4_text.py — Text analysis of a fixed string. Variant 11:
#                       a) word count
#                       b) longest word and its index
#                       c) every odd-positioned word (1st, 3rd, 5th, ...)
#                       No regular expressions used.
# Version: 1.0
# Developer: Student, Variant 11
# Date: 2025
# =============================================================================

from utils import print_separator

# Fixed source string (words separated by spaces and commas)
SOURCE_TEXT = (
    "So she was considering in her own mind, as well as she could, "
    "for the hot day made her feel very sleepy and stupid, whether "
    "the pleasure of making a daisy-chain would be worth the trouble "
    "of getting up and picking the daisies, when suddenly a White "
    "Rabbit with pink eyes ran close by her."
)


# ─────────────────────────────────────────────
#  TOKENISATION  (no regex)
# ─────────────────────────────────────────────

def extract_words(text):
    """
    Split the source text into a list of clean words.
    Separators are spaces and commas; trailing punctuation is stripped.
    No regular expressions are used.

    Args:
        text (str): The source string to tokenise.

    Returns:
        list[str]: Ordered list of words with punctuation removed.
    """
    # Characters to strip from both ends of each token
    strip_chars = " .,!?;:\"'()-"

    words = []
    # Split by spaces and commas
    for token in text.replace(",", " ").split():
        clean = token.strip(strip_chars)
        if clean:
            words.append(clean)
    return words


# ─────────────────────────────────────────────
#  SUBTASK A — word count
# ─────────────────────────────────────────────

def count_words(words):
    """
    Return the total number of words in the list.

    Args:
        words (list[str]): List of words.

    Returns:
        int: Total word count.
    """
    return len(words)


# ─────────────────────────────────────────────
#  SUBTASK B — longest word and its position
# ─────────────────────────────────────────────

def find_longest_word(words):
    """
    Find the longest word in the list and its 1-based ordinal position.
    If several words share the maximum length, the first one is returned.

    Args:
        words (list[str]): List of words.

    Returns:
        tuple[str, int]: (longest_word, 1-based position).
    """
    longest     = words[0]
    longest_idx = 0

    for i, word in enumerate(words[1:], start=1):
        if len(word) > len(longest):
            longest     = word
            longest_idx = i

    return longest, longest_idx + 1   # convert to 1-based


# ─────────────────────────────────────────────
#  SUBTASK C — every odd-positioned word
# ─────────────────────────────────────────────

def get_odd_words(words):
    """
    Return every odd-positioned word from the list.
    Position numbering starts at 1, so words at positions 1, 3, 5, ...
    are returned (indices 0, 2, 4, ... in the list).

    Args:
        words (list[str]): List of words.

    Returns:
        list[tuple[int, str]]: List of (1-based position, word) pairs.
    """
    result = []
    for i, word in enumerate(words):
        if i % 2 == 0:           # index 0, 2, 4, … → positions 1, 3, 5, …
            result.append((i + 1, word))
    return result


# ─────────────────────────────────────────────
#  OUTPUT
# ─────────────────────────────────────────────

def print_source(text):
    """
    Display the source string in a readable wrapped format.

    Args:
        text (str): The source string.
    """
    print(f"\n  Исходный текст:\n  \"{text}\"\n")


def print_word_count(total):
    """
    Display the total word count result.

    Args:
        total (int): Number of words.
    """
    print("  ── а) Количество слов ─────────────────────────")
    print(f"  Слов в строке : {total}")


def print_longest(word, position):
    """
    Display the longest word and its ordinal number.

    Args:
        word     (str): The longest word.
        position (int): Its 1-based position in the word list.
    """
    print("\n  ── б) Самое длинное слово ─────────────────────")
    print(f"  Слово         : '{word}'")
    print(f"  Длина         : {len(word)} символов")
    print(f"  Порядковый №  : {position}")


def print_odd_words(odd_words):
    """
    Display every odd-positioned word with its position number.

    Args:
        odd_words (list[tuple[int, str]]): List of (position, word) pairs.
    """
    print("\n  ── в) Слова на нечётных позициях (1-е, 3-е, 5-е, …) ─")
    for pos, word in odd_words:
        print(f"  Позиция {pos:>3} : {word}")


# ─────────────────────────────────────────────
#  MAIN TASK ENTRY POINT
# ─────────────────────────────────────────────

def run_task4():
    """
    Main entry point for Task 4.
    Analyses the fixed White Rabbit source string:
      a) counts all words,
      b) finds the longest word and its position,
      c) prints every odd-positioned word.
    No regular expressions are used.
    """
    print_separator("Задание 4 — Анализ текста (строка про Белого Кролика)")

    try:
        print_source(SOURCE_TEXT)

        words = extract_words(SOURCE_TEXT)

        # a) word count
        total = count_words(words)
        print_word_count(total)

        # b) longest word
        longest, position = find_longest_word(words)
        print_longest(longest, position)

        # c) odd-positioned words
        odd_words = get_odd_words(words)
        print_odd_words(odd_words)

    except ValueError as e:
        print(f"  [ошибка] Ошибка значения: {e}")
    except Exception as e:
        print(f"  [ошибка] Непредвиденная ошибка: {e}")

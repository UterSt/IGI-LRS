"""
task2_main.py — Entry point for Task 2: Regex text analysis (Variant 11).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Flow:
  1. Read text from data/sample_text.txt
  2. Run general analysis  + variant-11 analysis
  3. Ask user to validate a 6-digit number (variant-11 check)
  4. Save results to output/task2_results.txt
  5. Archive with zipfile and show archive info
"""

import os
import zipfile
from datetime import datetime

from utils import print_separator, input_string_nonempty, ensure_dir
from task2_regex.general_analysis import TextAnalyzer
from task2_regex.var11_analysis   import Variant11Analyzer

TEXT_FILE   = "data/sample_text.txt"
RESULT_FILE = "output/task2_results.txt"
ARCHIVE     = "output/task2_results.zip"


# ─────────────────────────────────────────────
#  FILE I/O
# ─────────────────────────────────────────────

def read_text(path: str) -> str:
    """
    Read and return the content of a text file.

    Args:
        path (str): Path to the source text file.

    Returns:
        str: File contents.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Text file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_results(path: str, lines: list[str]) -> None:
    """
    Write analysis result lines to a file.

    Args:
        path  (str):       Destination file path.
        lines (list[str]): Lines to write.
    """
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n  [Файл] Результаты сохранены → {path}")


def archive_result(result_path: str, archive_path: str) -> None:
    """
    Add a result file to a ZIP archive and print archive metadata.

    Args:
        result_path  (str): Path to the file being archived.
        archive_path (str): Destination ZIP path.
    """
    ensure_dir(os.path.dirname(archive_path))
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(result_path, arcname=os.path.basename(result_path))

    print(f"  [ZIP]  Архив создан → {archive_path}")

    #zipinfo
    with zipfile.ZipFile(archive_path, "r") as zf:
        for info in zf.infolist():
            print(f"\n  Содержимое архива:")
            print(f"    Имя файла        : {info.filename}")
            print(f"    Исходный размер  : {info.file_size} байт")
            print(f"    Сжатый размер    : {info.compress_size} байт")
            ratio = (1 - info.compress_size / info.file_size) * 100 if info.file_size else 0
            print(f"    Степень сжатия   : {ratio:.1f}%")
            ts = datetime(*info.date_time)
            print(f"    Дата изменения   : {ts.strftime('%Y-%m-%d %H:%M:%S')}")


# ─────────────────────────────────────────────
#  RESULT BUILDER
# ─────────────────────────────────────────────

def build_result_lines(analyzer: Variant11Analyzer) -> list[str]:
    """
    Build a list of text lines representing the full analysis output.

    Args:
        analyzer (Variant11Analyzer): Fully run analyser.

    Returns:
        list[str]: Lines ready for writing to a file.
    """
    s  = analyzer.stats
    r  = analyzer.v11_results
    lines = [
        "=" * 60,
        "  ЛР4 — Задание 2. Анализ текста (Вариант 11)",
        "=" * 60,
        "",
        "── ОБЩАЯ СТАТИСТИКА ──",
        f"  Всего предложений        : {s.sentences.total}",
        f"    Повествовательных (.)  : {s.sentences.declarative}",
        f"    Вопросительных    (?)  : {s.sentences.interrogative}",
        f"    Побудительных     (!)  : {s.sentences.imperative}",
        f"  Средняя длина предложения: {s.avg_sent_len} симв.",
        f"  Средняя длина слова      : {s.avg_word_len} симв.",
        f"  Найдено смайликов        : {s.smiley_count}",
        "",
        "── ВАРИАНТ 11: Слова с [a-o] И цифрой ──",
    ] + [f"  {w}" for w in r["ao_digit_words"]] + [
        "",
        "── ВАРИАНТ 11: Слова в кавычках ──",
        f"  Количество: {r['quoted_count']}",
    ] + [f"  \"{q}\"" for q in r["quoted_phrases"]] + [
        "",
        "── ВАРИАНТ 11: Частота букв ──",
    ] + [f"  {ch}: {cnt}" for ch, cnt in r["letter_frequency"].items()] + [
        "",
        "── ВАРИАНТ 11: Словосочетания через запятую (по алфавиту) ──",
    ] + [f"  {i+1:>3}. {p}" for i, p in enumerate(r["comma_phrases"])]

    return lines


# ─────────────────────────────────────────────
#  SIX-DIGIT CHECK (interactive)
# ─────────────────────────────────────────────

def interactive_six_digit_check(analyzer: Variant11Analyzer) -> None:
    """
    Prompt the user for a string and tell them whether it is a valid
    6-digit number (variant 11 regex check).

    Args:
        analyzer (Variant11Analyzer): Instance used for the check.
    """
    print("\n  ── Вариант 11: Проверка шестизначного числа ──")
    print("  (Корректное число — без ведущих нулей, например 123456)")
    user_input = input_string_nonempty("  Введите строку для проверки: ")
    valid = analyzer.check_six_digit_number(user_input)
    verdict = "✔  КОРРЕКТНОЕ шестизначное число" if valid else "✘  НЕ является шестизначным числом"
    print(f"  '{user_input}' → {verdict}")


# ─────────────────────────────────────────────
#  MAIN TASK ENTRY POINT
# ─────────────────────────────────────────────

def run_task2() -> None:
    """
    Main entry point for Task 2 — Regex text analysis.

    Reads a text file, runs general + variant-11 analyses,
    performs an interactive 6-digit check, saves results,
    and archives the output with zipfile.
    """
    print_separator("Задание 2 — Анализ текста (Вариант 11)")

    try:
        text = read_text(TEXT_FILE)
    except FileNotFoundError as e:
        print(f"  [ОШИБКА] {e}")
        return

    print(f"  Исходный файл: {TEXT_FILE}")
    print(f"  Символов     : {len(text)}")

    analyzer = Variant11Analyzer(text)
    print(f"\n  Анализатор: {analyzer}")

    analyzer.run_general_analysis()
    analyzer.print_general_stats()

    analyzer.run_variant_analysis()
    analyzer.print_variant_results()

    # ── interactive check ──────────────────────────────
    interactive_six_digit_check(analyzer)

    # ── save + archive ─────────────────────────────────
    lines = build_result_lines(analyzer)
    save_results(RESULT_FILE, lines)
    archive_result(RESULT_FILE, ARCHIVE)

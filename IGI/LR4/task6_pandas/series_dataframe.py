"""
series_dataframe.py — Задание А: Series and DataFrame demo (Task 6, Variant 11).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Variant 11 specific task:
  Создайте DataFrame player_sample из 5 случайных строк.
  Оставьте только столбцы Name, Age, Overall. Сбросьте индекс.

Also demonstrates all required pandas А-topics:
  1. Импорт библиотеки Pandas
  2. Структура Series
  3. Создание Series
  4. Функция display (аналог)
  5. Доступ через .loc и .iloc
  6. Объект DataFrame. Создание.
"""

import pandas as pd
import numpy as np
from task6_pandas.data_loader import BaseDataAnalyzer


class SeriesDataFrameDemo(BaseDataAnalyzer):
    """
    Demonstrates Pandas Series and DataFrame basics for Задание А.

    Inherits BaseDataAnalyzer (super() in __init__).
    Polymorphism: __str__ overridden.
    """

    _task_name: str = "Задание А — Series и DataFrame"   # static attribute

    def __init__(self, df: pd.DataFrame):
        """
        Initialise demo with a source DataFrame.

        Args:
            df (pd.DataFrame): The FIFA 19 DataFrame.
        """
        super().__init__(df)                            # super() → BaseDataAnalyzer

    # ── class method ───────────────────────────────────

    @classmethod
    def get_task_name(cls) -> str:
        """Return the name of this demonstration."""
        return cls._task_name

    # ── 1. Import (documented for reference) ──────────

    @staticmethod
    def show_import() -> None:
        """
        Demonstrate pandas import.
        In real code: import pandas as pd
        """
        print("\n  1. Импорт библиотеки:")
        print("     import pandas as pd")
        print(f"     Версия: {pd.__version__}")

    # ── 2 + 3. Series creation ─────────────────────────

    def create_series_examples(self) -> dict[str, pd.Series]:
        """
        Create and return example Series objects.

        Returns:
            dict: Named Series objects for demonstration.
        """
        # From list
        overall_sample = self._df["Overall"].head(5)
        s_list = pd.Series(
            overall_sample.values,
            index=[f"Игрок_{i+1}" for i in range(5)],
            name="Overall_рейтинг",
        )

        # From dict
        s_dict = pd.Series(
            {"Messi": 94, "Ronaldo": 94, "Neymar": 92,
             "Salah": 90, "De Bruyne": 91},
            name="Топ_игроки",
        )

        # From DataFrame column
        s_col = self._df["SprintSpeed"].rename("SprintSpeed_Series")

        return {
            "из_списка": s_list,
            "из_словаря": s_dict,
            "из_столбца": s_col,
        }

    def print_series_examples(self) -> None:
        """Print all Series examples with explanations."""
        examples = self.create_series_examples()

        print("\n  2-3. Создание Series:")
        print()
        for name, s in examples.items():
            print(f"     # Series {name}:")
            print(f"     pd.Series(name='{s.name}', dtype={s.dtype})")
            print(s.head(5).to_string(header=True))
            print()

    # ── 4. display() ───────────────────────────────────

    def display(self, obj, title: str = "") -> None:
        """
        Analogue of Jupyter display() for console output.

        In Jupyter: display(df) shows a styled table.
        In console: we print with a formatted header.

        Args:
            obj:   Any pandas object (Series or DataFrame).
            title: Optional label.
        """
        if title:
            print(f"\n     [ display: {title} ]")
        if isinstance(obj, pd.DataFrame):
            print(obj.to_string(max_rows=10))
        elif isinstance(obj, pd.Series):
            print(obj.to_string())
        else:
            print(obj)

    # ── 5. .loc / .iloc ────────────────────────────────

    def demo_loc_iloc(self) -> None:
        """
        Demonstrate .loc (label-based) and .iloc (integer-based) access.
        """
        s = self.create_series_examples()["из_словаря"]

        print("\n  5. Доступ к элементам Series:")
        print()

        # .iloc — by integer position
        print("     # .iloc — по позиции (целое число):")
        print(f"     s.iloc[0]  -> {s.iloc[0]}  (первый элемент)")
        print(f"     s.iloc[-1] -> {s.iloc[-1]}  (последний элемент)")
        print(f"     s.iloc[1:3] ->\n{s.iloc[1:3].to_string()}")
        print()

        # .loc — by label
        print("     # .loc — по метке (индексу):")
        print(f"     s.loc['Messi']   -> {s.loc['Messi']}")
        print(f"     s.loc['Ronaldo'] -> {s.loc['Ronaldo']}")

        # Same on DataFrame
        df_head = self._df[["Name", "Age", "Overall"]].head(6).reset_index()
        print()
        print("     # .iloc на DataFrame:")
        print(f"     df.iloc[0, 0] -> {df_head.iloc[0, 1]!r}  (строка 0, столбец Name)")
        print(f"     df.iloc[2, :]  -> {df_head.iloc[2][['Name','Age','Overall']].to_dict()}")

    # ── 6. DataFrame creation ──────────────────────────

    def demo_dataframe_creation(self) -> None:
        """
        Demonstrate DataFrame creation methods.
        """
        print("\n  6. Создание DataFrame:")
        print()

        # From dict
        d = {"Имя": ["Месси", "Роналду"], "Возраст": [36, 38], "Рейтинг": [94, 93]}
        df_dict = pd.DataFrame(d)
        print("     # Из словаря:")
        self.display(df_dict, "DataFrame из словаря")

        # From numpy
        arr = np.array([[90, 75, 82], [85, 90, 78]])
        df_np = pd.DataFrame(arr, columns=["Скорость", "Агрессия", "Удар"],
                              index=["Нападающий", "Защитник"])
        print()
        print("     # Из NumPy-массива:")
        self.display(df_np, "DataFrame из NumPy")

    # ── Variant 11 specific task ───────────────────────

    def variant_task(self) -> pd.DataFrame:
        """
        Выполнить задание А варианта 11:
          Создать DataFrame player_sample из 5 случайных строк.
          Оставить только столбцы Name, Age, Overall.
          Сбросить индекс.

        Returns:
            pd.DataFrame: Resulting player_sample.
        """
        # Sample 5 random rows
        player_sample = self._df.sample(n=5, random_state=42)

        # Keep only needed columns
        cols_needed = [c for c in ["Name", "Age", "Overall"]
                       if c in player_sample.columns]
        player_sample = player_sample[cols_needed]

        # Reset index (drop old index)
        player_sample = player_sample.reset_index(drop=True)

        return player_sample

    def print_variant_task(self) -> None:
        """Print the Variant 11 specific task and its result."""
        print("\n  ── Вариант 11: Задание А ──")
        print("  Создать DataFrame из 5 случайных строк,")
        print("  оставить [Name, Age, Overall], сбросить индекс.\n")

        result = self.variant_task()
        self.display(result, "player_sample (5 строк, индекс сброшен)")

        print()
        print(f"     Тип:  {type(result).__name__}")
        print(f"     Форма: {result.shape}")
        print(f"     Индекс: {list(result.index)}")
        print(f"     Столбцы: {list(result.columns)}")

    # ── polymorphic __str__ ────────────────────────────

    def __str__(self) -> str:
        return (f"SeriesDataFrameDemo("
                f"строк={self.shape[0]}, "
                f"задача='{self._task_name}')")

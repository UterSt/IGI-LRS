"""
stats_analysis.py — Задание Б: Statistical analysis on FIFA 19 (Task 6, Variant 11).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Задание Б variant 11:
  1. Получение информации о датафрейме (по каждому параметру)
  2. Какова средняя скорость (SprintSpeed) футболистов,
     чья зарплата (Wage) ниже среднего? Ответ округлить до сотых.
  3. Во сколько раз средняя сила удара (ShotPower) самых агрессивных
     игроков (Aggression == max) выше, чем у наименее агрессивных?
"""

import pandas as pd
from task6_pandas.data_loader import BaseDataAnalyzer


class StatisticalAnalyzer(BaseDataAnalyzer):
    """
    Performs statistical analysis on the FIFA 19 DataFrame.

    Inherits BaseDataAnalyzer (super() in __init__).
    Polymorphism: overrides __str__.
    """

    _task_name: str = "Задание Б — Статистический анализ"   # static attribute

    def __init__(self, df: pd.DataFrame):
        """
        Initialize the analyzer with the FIFA 19 DataFrame.

        Args:
            df (pd.DataFrame): The FIFA 19 data.
        """
        super().__init__(df)                     # super() → BaseDataAnalyzer

    # ── class method ───────────────────────────────────

    @classmethod
    def get_task_name(cls) -> str:
        """Return the name of this task."""
        return cls._task_name

    # ── Part 1: DataFrame info ──────────────────────────

    def print_dataframe_info(self) -> None:
        """
        Display comprehensive info about the DataFrame:
        shape, dtypes, head, describe, columns, null values.
        """
        df = self._df
        print("\n  ── Информация о датафрейме ──")

        print(f"\n     df.shape       : {df.shape}  "
              f"(строк={df.shape[0]}, столбцов={df.shape[1]})")

        print(f"\n     df.columns     :\n     {list(df.columns)}")

        print(f"\n     df.dtypes      :")
        for col, dtype in df.dtypes.items():
            print(f"       {col:<15}: {dtype}")

        print(f"\n     df.head(3)     :")
        print(df.head(3).to_string(index=True))

        print(f"\n     df.info()      :")
        print(f"       Всего строк     : {len(df)}")
        print(f"       Пропущенных знач.: {df.isnull().sum().sum()}")
        for col in df.columns:
            n_null = df[col].isnull().sum()
            print(f"       {col:<15}: {df[col].dtype}  "
                  f"(пропусков: {n_null})")

        print(f"\n     df.describe()  :")
        num_cols = df.select_dtypes(include="number").columns.tolist()
        if num_cols:
            desc = df[num_cols].describe().round(2)
            print(desc.to_string())

    # ── Part 2: Avg SprintSpeed where Wage < mean ──────

    def avg_sprint_speed_below_avg_wage(self) -> float:
        """
        Calculate average SprintSpeed for players
        whose Wage is BELOW the overall average wage.

        Returns:
            float: Average SprintSpeed, rounded to 2 decimal places.
        """
        df = self._df
        if "Wage" not in df or "SprintSpeed" not in df:
            raise KeyError("Датафрейм не содержит столбцы Wage или SprintSpeed.")

        avg_wage = df["Wage"].mean()
        below_avg = df[df["Wage"] < avg_wage]
        result = below_avg["SprintSpeed"].mean()
        return round(float(result), 2)

    def print_sprint_speed_task(self) -> None:
        """Print the result of task 2 (SprintSpeed analysis)."""
        df = self._df
        avg_wage = df["Wage"].mean()
        below_avg = df[df["Wage"] < avg_wage]

        print("\n  ── Задание Б-2: SprintSpeed игроков с зарплатой ниже среднего ──")
        print(f"\n     Средняя зарплата всех игроков : {avg_wage:,.0f} €")
        print(f"     Игроков с зарплатой ниже ср.  : {len(below_avg)}")
        print(f"     Всего игроков                 : {len(df)}")

        result = self.avg_sprint_speed_below_avg_wage()
        print(f"\n     Средняя скорость (SprintSpeed) : {result}")
        print(f"     (у игроков с Wage < {avg_wage:,.0f} €)")

    # ── Part 3: ShotPower ratio max/min aggression ─────

    def shotpower_ratio_aggression(self) -> dict:
        """
        Calculate how many times average ShotPower of most aggressive players
        (Aggression == max) is higher than least aggressive (Aggression == min).

        Returns:
            dict: Result info with ratio, means, and aggression values.
        """
        df = self._df
        required = ["Aggression", "ShotPower"]
        for col in required:
            if col not in df.columns:
                raise KeyError(f"Столбец '{col}' отсутствует в датафрейме.")

        agg_max = df["Aggression"].max()
        agg_min = df["Aggression"].min()

        most_aggressive  = df[df["Aggression"] == agg_max]
        least_aggressive = df[df["Aggression"] == agg_min]

        sp_max_agg = most_aggressive["ShotPower"].mean()
        sp_min_agg = least_aggressive["ShotPower"].mean()

        ratio = (sp_max_agg / sp_min_agg) if sp_min_agg != 0 else float("inf")

        return {
            "agg_max":      int(agg_max),
            "agg_min":      int(agg_min),
            "count_max":    len(most_aggressive),
            "count_min":    len(least_aggressive),
            "sp_max_agg":   round(float(sp_max_agg), 2),
            "sp_min_agg":   round(float(sp_min_agg), 2),
            "ratio":        round(float(ratio), 2),
        }

    def print_shotpower_task(self) -> None:
        """Print the result of task 3 (ShotPower ratio analysis)."""
        r = self.shotpower_ratio_aggression()

        print("\n  ── Задание Б-3: ShotPower самых/наименее агрессивных ──")
        print()
        print(f"     Максимальная агрессия: {r['agg_max']}"
              f"  (таких игроков: {r['count_max']})")
        print(f"     Минимальная агрессия : {r['agg_min']}"
              f"  (таких игроков: {r['count_min']})")
        print()
        print(f"     Ср. ShotPower при Aggression={r['agg_max']}: {r['sp_max_agg']}")
        print(f"     Ср. ShotPower при Aggression={r['agg_min']}: {r['sp_min_agg']}")
        print()
        print(f"     Ответ: в {r['ratio']} раза выше")
        print(f"     ({r['sp_max_agg']} / {r['sp_min_agg']} = {r['ratio']})")

    # ── Polymorphic __str__ ────────────────────────────

    def __str__(self) -> str:
        return (f"StatisticalAnalyzer("
                f"строк={self.shape[0]}, "
                f"задача='{self._task_name}')")

"""
data_loader.py — FIFA 19 dataset loader for Task 6 (Variant 11).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Loads the real FIFA 19 dataset (fifa19.csv) if available,
otherwise generates a realistic synthetic dataset for demonstration.

Real dataset: https://www.kaggle.com/datasets/karangadiya/fifa19
Download 'data.csv', rename to 'data/fifa19.csv', then run again.
"""

import os
import numpy as np
import pandas as pd


# ─────────────────────────────────────────────
#  MIXIN
# ─────────────────────────────────────────────

class LogMixin:
    """Mixin: console logging with class prefix."""

    _log_on: bool = True       # static attribute

    def log(self, msg: str) -> None:
        """Print a log message."""
        if self._log_on:
            print(f"  [ЛОГ | {self.__class__.__name__}] {msg}")


# ─────────────────────────────────────────────
#  BASE ANALYZER
# ─────────────────────────────────────────────

class BaseDataAnalyzer(LogMixin):
    """
    Base class for pandas data analysis.

    Demonstrates static/dynamic attributes, magic methods,
    property with getter/setter.
    """

    _analyzer_count: int = 0      # static attribute

    def __init__(self, df: pd.DataFrame = None):
        self._df: pd.DataFrame = df      # dynamic attribute
        BaseDataAnalyzer._analyzer_count += 1

    # ── properties ─────────────────────────────────────

    @property
    def df(self) -> pd.DataFrame:
        """The DataFrame being analysed."""
        return self._df

    @df.setter
    def df(self, value: pd.DataFrame) -> None:
        if not isinstance(value, pd.DataFrame):
            raise TypeError("Ожидается pd.DataFrame.")
        self._df = value
        self.log("DataFrame обновлён.")

    @property
    def shape(self) -> tuple:
        """Shape of the DataFrame."""
        return self._df.shape if self._df is not None else (0, 0)

    # ── class method ───────────────────────────────────

    @classmethod
    def get_analyzer_count(cls) -> int:
        """Return how many analyzers have been created."""
        return cls._analyzer_count

    # ── magic methods ──────────────────────────────────

    def __len__(self) -> int:
        return len(self._df) if self._df is not None else 0

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"строк={self.shape[0]}, столбцов={self.shape[1]})")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(shape={self.shape})"

    def __contains__(self, col: str) -> bool:
        """'Wage' in analyzer."""
        return self._df is not None and col in self._df.columns


# ─────────────────────────────────────────────
#  FIFA 19 DATA LOADER
# ─────────────────────────────────────────────

class FIFADataLoader(BaseDataAnalyzer):
    """
    Loads the FIFA 19 dataset.

    If the real CSV is not found, creates a synthetic dataset
    with the same structure for demonstration purposes.

    Real dataset: https://www.kaggle.com/datasets/karangadiya/fifa19
    Place the downloaded 'data.csv' at:  LR4/data/fifa19.csv
    """

    # static attributes
    DEFAULT_PATH: str   = "data/fifa19.csv"
    REQUIRED_COLS: list = [
        "Name", "Age", "Overall", "Nationality",
        "Club", "Wage", "SprintSpeed", "Aggression", "ShotPower",
    ]
    _SYNTHETIC_NAMES: list = [
        "Messi", "Ronaldo", "Neymar", "Salah", "De Bruyne",
        "Modric", "Kante", "Alisson", "VanDijk", "Hazard",
        "Benzema", "Griezmann", "Pogba", "Lewandowski", "Suarez",
        "Firmino", "Henderson", "Mane", "Sterling", "Aguero",
        "Iniesta", "Busquets", "Alba", "Pique", "Ramos",
        "Varane", "Casemiro", "Kroos", "Bale", "Marcelo",
        "Koulibaly", "Navas", "Coutinho", "Dybala", "Icardi",
        "Higuain", "Boateng", "Muller", "Kimmich", "Neuer",
        "Thiago", "Cech", "Terry", "Lampard", "Gerrard",
        "Rooney", "Giggs", "Beckham", "Scholes", "Ferdinand",
    ]

    def __init__(self, path: str = ""):
        super().__init__()                            # super() call
        self._path: str = path or self.DEFAULT_PATH  # dynamic attribute
        self._synthetic: bool = False

    # ── property ───────────────────────────────────────

    @property
    def is_synthetic(self) -> bool:
        """True if a synthetic dataset is being used."""
        return self._synthetic

    @property
    def path(self) -> str:
        """Path to the CSV file."""
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        if not value.strip():
            raise ValueError("Путь не может быть пустым.")
        self._path = value.strip()

    # ── static helper ──────────────────────────────────

    @staticmethod
    @staticmethod
    def _parse_wage(value):
        """Convert '€565K' -> 565000, '€1M' -> 1000000"""
        if pd.isna(value) or value == 0:
            return 0
        # Убираем € в любой кодировке (latin-1 даёт \x80 вместо €)
        s = str(value).replace('€', '').replace('\x80', '').strip()
        if 'K' in s:
            return float(s.replace('K', '')) * 1000
        if 'M' in s:
            return float(s.replace('M', '')) * 1_000_000
        try:
            return float(s)
        except ValueError:
            return 0

    # ── load ───────────────────────────────────────────

    def load(self) -> pd.DataFrame:
        """
        Load the FIFA 19 dataset from CSV, or generate a synthetic one.

        Returns:
            pd.DataFrame: Loaded or synthetic DataFrame.
        """
        if os.path.exists(self._path):
            self.log(f"Загрузка реального датасета: {self._path}")
            df = pd.read_csv(self._path, low_memory=False, encoding="latin-1")

            # Parse wage to numeric
            if "Wage" in df.columns:
                df["Wage"] = df["Wage"].apply(self._parse_wage)

            # Keep only needed columns (those that exist)
            available = [c for c in self.REQUIRED_COLS if c in df.columns]
            df = df[available].copy()

            self._df = df
            self._synthetic = False
            self.log(f"Загружено {len(df)} строк, {len(df.columns)} столбцов.")
        else:
            self.log(f"Файл не найден: {self._path}")
            self.log("Создаётся синтетический датасет для демонстрации.")
            self._df = self._generate_synthetic()
            self._synthetic = True

        return self._df

    def _generate_synthetic(self, n: int = 200) -> pd.DataFrame:
        """
        Generate a synthetic FIFA 19-like DataFrame.

        Args:
            n (int): Number of rows.

        Returns:
            pd.DataFrame: Synthetic dataset.
        """
        rng = np.random.default_rng(42)
        names = (self._SYNTHETIC_NAMES * (n // len(self._SYNTHETIC_NAMES) + 1))[:n]

        wages_raw = rng.integers(5, 300, size=n) * 1000   # 5K–300K
        aggression = rng.integers(30, 100, size=n)

        return pd.DataFrame({
            "Name":        names,
            "Age":         rng.integers(17, 38, size=n),
            "Overall":     rng.integers(55, 99, size=n),
            "Nationality": rng.choice(["Spain", "France", "Brazil",
                                       "Argentina", "Germany", "England"], size=n),
            "Club":        rng.choice(["Barcelona", "Real Madrid", "PSG",
                                       "Liverpool", "ManCity", "Chelsea"], size=n),
            "Wage":        wages_raw.astype(float),
            "SprintSpeed": rng.integers(40, 99, size=n),
            "Aggression":  aggression,
            "ShotPower":   rng.integers(30, 99, size=n),
        })

    def __repr__(self) -> str:
        mode = "synthetic" if self._synthetic else "real"
        return f"FIFADataLoader(path={self._path!r}, mode={mode})"

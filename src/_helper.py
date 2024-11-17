from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterator, List
import csv

if TYPE_CHECKING:
    import pandas as pd
    from pathlib import Path

class ToPD(ABC):
    @abstractmethod
    def to_pd(self) -> "pd.DataFrame": ...

class ToFile(ABC):
    @abstractmethod
    def to_file(self, path: "Path") -> None: ...


class DataConverter(ToPD, ToFile):
    def __init__(
        self, stats_iter: Iterator[dict], header: List[str]
    ):
        self._stats_iter = stats_iter
        self._header = header

    def to_pd(self):
        df = pd.DataFrame.from_records(list(self._stats_iter))
        if df.empty:
            return pd.DataFrame(columns=self._header)
        return df.rename(columns={k: v for k, v in zip(df.columns, self._header)})

    def to_file(self, path: Path):
        with path.open("w") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(self._header)
            for stats in self._stats_iter:
                csv_writer.writerow(stats.values())


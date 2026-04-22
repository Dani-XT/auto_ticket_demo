import polars as pl

from dataclasses import dataclass
from pathlib import Path

from src.models.ticket_job import TicketJob

@dataclass
class ExcelResult:
    excel_path: Path
    df: pl.DataFrame
    jobs: list[TicketJob]
    col_map: dict[str, int]

    @property
    def total_jobs(self) -> int:
        return len(self.jobs)


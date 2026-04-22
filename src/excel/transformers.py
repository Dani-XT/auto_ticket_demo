from datetime import datetime, date, time
import polars as pl

from src.utils.exceptions import ExcelHeaderError, ExcelNoPendingJobsError, ExcelRequiredColumnsError, ExcelFormatError
from src.utils.datetime_utils import parse_text_datetime

from src.models.ticket_job import TicketJob

from src.excel.schema import REQUIRED_COLUMNS
from src.excel.schema import TICKET_COLUMNS


# devuelve la ubicacion del header
def get_i_header(df_raw: pl.DataFrame):
    try:
        req_col = {r.strip().upper() for r in REQUIRED_COLUMNS}
        ticket_col = {t.strip().upper() for t in TICKET_COLUMNS}

        for i, row in enumerate(df_raw.iter_rows()):
            norm = {str(c).strip().upper() for c in row if c is not None and str(c).strip() != ""}
            if req_col.issubset(norm) and (norm & ticket_col):
                return i

        raise ExcelHeaderError("No se encontro el header")
            
    except Exception as e:
         raise ExcelHeaderError(f"Ocurrio un error identificando el header {str(e)}")

# devuelve y elimina los datos que no correspondan al header
def get_df_raw_data(df_raw: pl.DataFrame, i_header: int,):
    try:
        data_cols = df_raw.columns[1:]
        header_cells = list(df_raw.row(i_header))[1:]

        required_set = {c.strip().upper() for c in REQUIRED_COLUMNS}
        ticket_set = {c.strip().upper() for c in TICKET_COLUMNS}

        rename_map: dict[str, str] = {}
        col_map: dict[str, int] = {}
        keep_cols: list[str] = []

        for col, cell in zip(data_cols, header_cells):
            name = "" if cell is None else str(cell).strip().upper()
            if not name or name == "NONE":
                continue

            if name in required_set:
                keep_cols.append(col)
                rename_map[col] = name
            
            elif name in ticket_set:
                keep_cols.append(col)
                rename_map[col] = "TICKET"

        df_data = (df_raw.slice(i_header + 1).select(["EXCEL_ROW"] + keep_cols).rename(rename_map))

        for col, header in rename_map.items():
            idx = int(col.split("_")[1])
            col_map[header] = idx

        return df_data, col_map
        
    except Exception as e:
        raise ExcelRequiredColumnsError(f"No se encontraron las columnas requeridas {str(e)}")

def split_web_creation_dt(text: str) -> tuple[date, time]:
    dt = parse_text_datetime(text)
    return dt.date(), dt.time()

# Detecta el formato y lo desplaza
def prepare_by_format(df_data: pl.DataFrame):
    try:
        first = normalize_fecha_hora_polars(df_data.head(1))

        fecha_ok = first.select(pl.col("FECHA").is_not_null()).item()
        hora_ok  = first.select(pl.col("HORA").is_not_null()).item()

        # Si no parsea FECHA/HORA => era descripción => quitar primera fila
        if not (fecha_ok and hora_ok):
            return df_data.slice(1)
        
        return df_data
    except Exception as e:
        raise ExcelFormatError(f"No se pudo identificar el formato del Excel: {str(e)}")

def normalize_fecha_hora_polars(df: pl.DataFrame, fecha_col: str = "FECHA", hora_col: str = "HORA",) -> pl.DataFrame:
    exprs: list[pl.Expr] = []

    if fecha_col in df.columns:
        fecha_txt = (
            pl.col(fecha_col)
            .cast(pl.Utf8, strict=False)
            .str.strip_chars()
        )

        exprs.append(
            pl.coalesce(
                fecha_txt.str.extract(r"(\d{4}-\d{2}-\d{2})")
                .str.strptime(pl.Date, "%Y-%m-%d", strict=False),

                fecha_txt.str.replace_all("-", "/")
                .str.strptime(pl.Date, "%d/%m/%Y", strict=False),

                pl.col(fecha_col).cast(pl.Date, strict=False),
                pl.col(fecha_col).cast(pl.Datetime, strict=False).dt.date(),
            ).alias(fecha_col)
        )

    if hora_col in df.columns:
        hora_txt = (
            pl.col(hora_col)
            .cast(pl.Utf8, strict=False)
            .str.strip_chars()
            .str.extract(r"(\d{2}:\d{2}(:\d{2})?)")
        )

        hora_txt = (
            pl.when(hora_txt.str.len_chars() == 5)
            .then(hora_txt + ":00")
            .otherwise(hora_txt)
        )

        exprs.append(
            hora_txt.str.strptime(pl.Time, "%H:%M:%S", strict=False).alias(hora_col)
        )

    return df.with_columns(exprs)


def filter_pending_tickets(df: pl.DataFrame,) -> pl.DataFrame:
    ticket_col = "TICKET"
    sol_col: str = "SOLUCION"

    ticket_txt = (
        pl.col(ticket_col)
        .cast(pl.Utf8, strict=False)
        .str.strip_chars()
        .fill_null("")
    )

    sol_txt = (
        pl.col(sol_col)
        .cast(pl.Utf8, strict=False)
        .str.strip_chars()
        .fill_null("")
    )

    ticket_empty = (ticket_txt == "") | (ticket_txt.str.to_uppercase() == "NONE")

    solution_ok = (sol_txt != "") & (sol_txt.str.to_uppercase() != "NONE")

    return df.filter(ticket_empty & solution_ok)

def dataframe_to_jobs(df: pl.DataFrame) -> list[TicketJob]:
    jobs: list[TicketJob] = []

    for row in df.iter_rows(named=True):
        row_id = int(row["EXCEL_ROW"])
        data = {k: v for k, v in row.items() if k != "EXCEL_ROW"}
        jobs.append(TicketJob(row_id=row_id, data=data))

    return jobs
    
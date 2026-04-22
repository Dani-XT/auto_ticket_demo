from datetime import datetime, date, time
import re

from src.utils.exceptions import ExcelError

def parse_excel_date_text(text: str) -> date | None:
    if text is None:
        return None
    s = str(text).strip()
    if not s:
        return None

    m = re.search(r"(\d{4}-\d{2}-\d{2})", s)
    if m:
        return datetime.strptime(m.group(1), "%Y-%m-%d").date()

    s2 = s.replace("-", "/")
    try:
        return datetime.strptime(s2, "%d/%m/%Y").date()
    except ValueError:
        return None
    
def parse_excel_time_text(text: str) -> time | None:
    if text is None:
        return None

    s = str(text).strip()
    if not s:
        return None

    m = re.search(r"(\d{2}:\d{2})(:\d{2})?", s)
    if not m:
        return None

    hhmm = m.group(1)
    ss = m.group(2) or ":00"

    try:
        return datetime.strptime(hhmm + ss, "%H:%M:%S").time()
    except ValueError:
        return None
    
def parse_text_datetime(text: str) -> datetime:
    if text is None:
        raise ExcelError("No hay ningun texto para parsear")
    
    fmts = [
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%dT%H:%M:%S",
    ]

    for fmt in fmts:
        try:
            return datetime.strptime(text.strip(), fmt)
        except ValueError:
            continue

    raise ExcelError(f"No pude parsear datetime: {text!r}")

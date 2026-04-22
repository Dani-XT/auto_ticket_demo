
from pathlib import Path
import logging


from src.excel.reader import (
    transform_excel_to_df,
)
from src.excel.validators import (
    validate_excel,
)

from src.excel.transformers import (
    normalize_fecha_hora_polars,
    filter_pending_tickets,
    get_i_header,
    prepare_by_format,
    get_df_raw_data,
    dataframe_to_jobs,
)

from src.models.excel_models import ExcelResult

from src.utils.exceptions import ExcelEmptyError, ExcelNoPendingJobsError

logger = logging.getLogger(__name__)

class ExcelService:
    # procesa excel de ticket para convertirlos en jobs y el sistema los pueda cargar
    def load_jobs(self, excel_path: Path,) -> ExcelResult:
        logger.info("Cargando Excel: %s", excel_path)
        
        
        validate_excel(excel_path)
        df_raw = transform_excel_to_df(excel_path)

        if df_raw.is_empty():
            logger.error("El archivo excel no contiene datos")
            raise ExcelEmptyError("El archivo Excel no contiene datos")
        
        i_header = get_i_header(df_raw=df_raw)
        df_raw_data, col_map = get_df_raw_data(df_raw=df_raw, i_header=i_header)


        # Limpia completamente quitando columnas de datos dependiendo del formato
        df_data = prepare_by_format(df_raw_data)
        df_data = normalize_fecha_hora_polars(df_data)
        df_data = filter_pending_tickets(df_data)

        if df_data.is_empty():
            raise ExcelNoPendingJobsError("La planilla no contiene tickets pendientes para cargar")
        
        jobs = dataframe_to_jobs(df_data)

        return ExcelResult(
            excel_path=excel_path,
            df=df_data,
            jobs=jobs,
            col_map=col_map,
        )
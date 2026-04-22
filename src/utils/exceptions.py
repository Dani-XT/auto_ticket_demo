# src/utils/exceptions.py

class AppError(Exception):
    default_title = "Error"
    default_level = "error"

    def __init__(self, message: str | None = None):
        self.message = message or "Ocurrió un error inesperado."
        super().__init__(self.message)

    @property
    def title(self) -> str:
        return self.default_title

    @property
    def level(self) -> str:
        return self.default_level

    def __str__(self) -> str:
        return self.message

class InternalError(AppError):
    default_title = "Ocurrio un error inesperado."

class ExcelResultEmpty(AppError):
    default_title = "Error con el Excel"

class ProcessRuninngError(AppError):
    default_title = "Proceso en ejecución"

# =========================
# EXCEL
# =========================
class ExcelError(AppError):
    default_title = "Error con el Excel"


class ExcelFileNotFoundError(ExcelError):
    pass


class ExcelFileOpenError(ExcelError):
    pass


class ExcelEmptyError(ExcelError):
    pass


class ExcelHeaderError(ExcelError):
    pass


class ExcelFormatError(ExcelError):
    pass


class ExcelRequiredColumnsError(ExcelError):
    pass


class ExcelNoPendingJobsError(ExcelError):
    pass


# =========================
# TEMPLATE EXCEL
# =========================
class TemplateError(AppError):
    default_title = "Error con la plantilla"


class TemplateNotFoundError(TemplateError):
    default_title = "Plantilla no encontrada"

# =========================
# ARCHIVOS README
# =========================
class HelpFileError(AppError):
    default_title = "Error con la ayuda"


class HelpFileNotFoundError(HelpFileError):
    default_title = "Archivo no encontrado"


class HelpFileOpenError(HelpFileError):
    default_title = "Error al abrir ayuda"


# =========================
# AUTENTICACIÓN / AUTOMATIZACIÓN
# =========================
class AuthenticationError(AppError):
    default_title = "Error de autenticación"


class AutomationError(AppError):
    default_title = "Error en automatización"


class TicketProcessError(AutomationError):
    default_title = "Error al procesar ticket"

class JobValidationError(TicketProcessError):
    pass

# =========================
# ESTADO
# =========================
class StateError(AppError):
    default_title = "Error de estado"

class RetryableUIError(TicketProcessError):
    default_title = "Error reintentable de interfaz"

class UncertainTicketCreationError(TicketProcessError):
    default_title = "Creación incierta de ticket"

class UncertainTicketCloseError(TicketProcessError):
    default_title = "Cierre incierto de ticket"
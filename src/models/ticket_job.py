from dataclasses import dataclass
from typing import Any
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "PENDIENTE"

    CREATE_IN_PROGRESS = "CREATE_IN_PROGRESS"
    CREATE_UNCERTAIN = "CREADO INCIERTO"
    CREATED = "CREADO"

    CLOSE_IN_PROGRESS = "CIERRE EN PROGRESO"
    CLOSE_UNCERTAIN = "CIERRE INCIERTO"
    CLOSED = "CERRADO"

    FAILED_CREATE = "FALLA AL CREAR"
    FAILED_CLOSE = "FALLA AL CERRAR"

# Modelo de la fila/ticket en memoria
@dataclass
class TicketJob:
    row_id: int
    data: dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    ticket_id: str | None = None
    error: str | None = None
    creation_dt_text: str | None = None

    @property
    def fecha(self):
        return self.data.get("FECHA")

    @property
    def hora(self):
        return self.data.get("HORA")

    @property
    def problema(self):
        return self.data.get("PROBLEMA")

    @property
    def solucion(self):
        return self.data.get("SOLUCION")

    @property
    def ticket(self):
        return self.data.get("TICKET")

    def needs_create(self) -> bool:
        return self.status in {
            JobStatus.PENDING,     
            JobStatus.CREATE_UNCERTAIN,
            JobStatus.FAILED_CREATE,
        }

    def is_finished(self) -> bool:
        return self.status == JobStatus.CLOSED
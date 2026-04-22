from dataclasses import dataclass


# Modelo del resultado del proceso, comunicacion directa entre el SERVICES Y FRAME

@dataclass(frozen=True)
class ProcessRowResult:
    row_id: int
    status: str
    ticket_id: str | None = None
    error: str | None = None

@dataclass(frozen=True)
class ProcessStatusUpdate:
    message: str
    processed: int = 0
    total: int = 0

@dataclass(frozen=True)
class ProcessCompleted:
    message: str
    processed: int
    total: int

@dataclass(frozen=True)
class ProcessFailed:
    title: str
    message: str
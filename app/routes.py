
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database import get_db
from app.schemas import (
    QueueCreate,
    QueueResponse,
    QueueStatusUpdate,
    QueueSummary,
)
from app import services

router = APIRouter(prefix="/api/v1", tags=["Antrian Klinik"])


@router.post(
    "/queues",
    response_model=QueueResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: QueueCreate,
    db: sqlite3.Connection = Depends(get_db),
):
    return services.register_queue(db, data)


@router.get("/queues/today", response_model=list[QueueResponse])
def list_today(
    db: sqlite3.Connection = Depends(get_db),
):
    return services.get_today_queues(db)


@router.get("/queues/{queue_id}", response_model=QueueResponse)
def detail(
    queue_id: int,
    db: sqlite3.Connection = Depends(get_db),
):
    try:
        return services.get_queue(db, queue_id)
    except services.QueueNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.post("/queues/call-next", response_model=QueueResponse)
def call_patient(
    poli: str = Query(min_length=2, max_length=50),
    db: sqlite3.Connection = Depends(get_db),
):
    try:
        return services.call_next(db, poli)
    except services.NoWaitingQueueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.patch(
    "/queues/{queue_id}/status",
    response_model=QueueResponse,
)
def change_status(
    queue_id: int,
    data: QueueStatusUpdate,
    db: sqlite3.Connection = Depends(get_db),
):
    try:
        return services.update_queue_status(db, queue_id, data)
    except services.QueueNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/summary/today", response_model=QueueSummary)
def summary(
    db: sqlite3.Connection = Depends(get_db),
):
    return services.get_today_summary(db)

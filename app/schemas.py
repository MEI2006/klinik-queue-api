
from typing import Literal
from pydantic import BaseModel, Field


StatusAntrian = Literal[
    "menunggu", "dipanggil", "dilayani",
    "selesai", "dibatalkan"
]


class QueueCreate(BaseModel):
    nama_pasien: str = Field(min_length=2, max_length=100)
    poli: str = Field(min_length=2, max_length=50)
    keluhan: str = Field(default="", max_length=500)


class QueueResponse(BaseModel):
    id: int
    nama_pasien: str
    poli: str
    keluhan: str
    tanggal: str
    nomor_antrian: int
    status: StatusAntrian
    created_at: str


class QueueStatusUpdate(BaseModel):
    status: StatusAntrian


class QueueSummary(BaseModel):
    tanggal: str
    total_antrian: int
    menunggu: int
    dipanggil: int
    dilayani: int
    selesai: int
    dibatalkan: int


from datetime import date

from app.schemas import QueueCreate, QueueStatusUpdate


class QueueNotFoundError(Exception):
    pass


class NoWaitingQueueError(Exception):
    pass


def row_to_dict(row):
    return dict(row) if row else None


def get_queue(db, queue_id: int):
    row = db.execute(
        "SELECT * FROM queues WHERE id = ?", (queue_id,)
    ).fetchone()

    if row is None:
        raise QueueNotFoundError("Antrian tidak ditemukan")

    return dict(row)


def register_queue(db, data: QueueCreate):
    today = date.today().isoformat()

    db.execute("BEGIN IMMEDIATE")

    row = db.execute(
        """SELECT COALESCE(MAX(nomor_antrian), 0) AS last_number
           FROM queues
           WHERE tanggal = ? AND poli = ?""",
        (today, data.poli),
    ).fetchone()

    next_number = row["last_number"] + 1

    cursor = db.execute(
        """INSERT INTO queues
           (nama_pasien, poli, keluhan, tanggal, nomor_antrian)
           VALUES (?, ?, ?, ?, ?)""",
        (
            data.nama_pasien,
            data.poli,
            data.keluhan,
            today,
            next_number,
        ),
    )

    queue_id = cursor.lastrowid
    db.commit()

    return get_queue(db, queue_id)


def get_today_queues(db):
    today = date.today().isoformat()

    rows = db.execute(
        """SELECT * FROM queues
           WHERE tanggal = ?
           ORDER BY poli, nomor_antrian""",
        (today,),
    ).fetchall()

    return [dict(row) for row in rows]


def call_next(db, poli: str):
    today = date.today().isoformat()

    db.execute("BEGIN IMMEDIATE")

    row = db.execute(
        """SELECT id FROM queues
           WHERE tanggal = ? AND poli = ? AND status = 'menunggu'
           ORDER BY nomor_antrian
           LIMIT 1""",
        (today, poli),
    ).fetchone()

    if row is None:
        db.rollback()
        raise NoWaitingQueueError(
            "Tidak ada pasien yang sedang menunggu di poli ini"
        )

    queue_id = row["id"]

    db.execute(
        "UPDATE queues SET status = 'dipanggil' WHERE id = ?",
        (queue_id,),
    )
    db.commit()

    return get_queue(db, queue_id)


def update_queue_status(
    db, queue_id: int, data: QueueStatusUpdate
):
    get_queue(db, queue_id)

    db.execute(
        "UPDATE queues SET status = ? WHERE id = ?",
        (data.status, queue_id),
    )
    db.commit()

    return get_queue(db, queue_id)


def get_today_summary(db):
    today = date.today().isoformat()

    row = db.execute(
        """SELECT
             COUNT(*) AS total_antrian,
             SUM(CASE WHEN status = 'menunggu' THEN 1 ELSE 0 END)
                 AS menunggu,
             SUM(CASE WHEN status = 'dipanggil' THEN 1 ELSE 0 END)
                 AS dipanggil,
             SUM(CASE WHEN status = 'dilayani' THEN 1 ELSE 0 END)
                 AS dilayani,
             SUM(CASE WHEN status = 'selesai' THEN 1 ELSE 0 END)
                 AS selesai,
             SUM(CASE WHEN status = 'dibatalkan' THEN 1 ELSE 0 END)
                 AS dibatalkan
           FROM queues
           WHERE tanggal = ?""",
        (today,),
    ).fetchone()

    result = dict(row)

    for key in (
        "total_antrian", "menunggu", "dipanggil",
        "dilayani", "selesai", "dibatalkan"
    ):
        result[key] = result[key] or 0

    result["tanggal"] = today
    return result

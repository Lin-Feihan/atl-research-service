import json
import os
import sqlite3
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]

DEFAULT_DB_PATH = (
    ROOT_DIR / "data" / "atl_runs.db"
)


def get_db_path():
    configured = os.getenv("SQLITE_PATH")

    if configured:
        path = Path(configured)

        if not path.is_absolute():
            path = ROOT_DIR / path
    else:
        path = DEFAULT_DB_PATH

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path


def connect():
    connection = sqlite3.connect(
        get_db_path(),
        timeout=30,
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_database():
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                status TEXT NOT NULL,
                settings_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                error TEXT,
                result_json TEXT
            )
            """
        )

        connection.commit()


def create_run_record(
    run_id,
    agent_id,
    status,
    settings,
    created_at,
):
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO runs (
                run_id,
                agent_id,
                status,
                settings_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                run_id,
                agent_id,
                status,
                json.dumps(
                    settings,
                    ensure_ascii=False,
                ),
                created_at,
            ),
        )

        connection.commit()


def get_run_record(run_id):
    with connect() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM runs
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchone()

    if row is None:
        return None

    return dict(row)


def update_run_status(
    run_id,
    status,
    error=None,
    completed_at=None,
):
    with connect() as connection:
        connection.execute(
            """
            UPDATE runs
            SET status = ?,
                error = ?,
                completed_at = ?
            WHERE run_id = ?
            """,
            (
                status,
                error,
                completed_at,
                run_id,
            ),
        )

        connection.commit()

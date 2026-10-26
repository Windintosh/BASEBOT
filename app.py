import sys
from pathlib import Path

BACK_DIR = Path(__file__).resolve().parent / "back"
sys.path.insert(0, str(BACK_DIR))

from back.main import app


@app.get("/probe/health")
def health():
    return {"status": "ok"}


@app.get("/probe")
def check_dependencies():
    import chromadb
    import sklearn
    import torch

    result = torch.tensor([2.0, 3.0]).sum().item()
    assert result == 5.0

    return {
        "status": "ok",
        "torch": torch.__version__,
        "chromadb": chromadb.__version__,
        "scikit_learn": sklearn.__version__,
    }

@app.get("/probe/db")
def check_database():
    from sqlalchemy import text
    # from back.database.db_connection import engine
    from back.database.db_connection import engine

    with engine.connect() as connection:
        table_count = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = DATABASE()
                  AND table_type = 'BASE TABLE'
            """)
        ).scalar_one()

        ssl_row = connection.exec_driver_sql(
            "SHOW SESSION STATUS LIKE 'Ssl_cipher'"
        ).first()
        ssl_enabled = bool(ssl_row and ssl_row[1])

        if not ssl_enabled:
            raise RuntimeError("Database SSL connection is required")

    return {
        "status": "ok",
        "table_count": table_count,
        "ssl": ssl_enabled,
    }
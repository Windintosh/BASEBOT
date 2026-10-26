import os
import shutil
import tempfile
from pathlib import Path


BACK_DIR = Path(__file__).resolve().parent
CHROMA_SOURCE_PATH = BACK_DIR / "chroma_db"

if not (CHROMA_SOURCE_PATH / "chroma.sqlite3").is_file():
    raise FileNotFoundError("배포에 사용할 ChromaDB 인덱스가 없습니다.")

CHROMA_PATH = CHROMA_SOURCE_PATH

if os.environ.get("VERCEL"):
    # shortcut: 실행 환경별 임시 복사본이며, 색인 갱신은 로컬 생성 후 재배포
    runtime_dir = Path(tempfile.mkdtemp(prefix="basebot_chroma_"))
    CHROMA_PATH = runtime_dir / "chroma_db"
    shutil.copytree(CHROMA_SOURCE_PATH, CHROMA_PATH)
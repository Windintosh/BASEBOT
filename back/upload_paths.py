import os
import tempfile
from pathlib import Path

BACK_DIR = Path(__file__).resolve().parent

# shortcut: Vercel 업로드는 임시 저장이며, 영구 보관이 필요하면 외부 저장소로 전환
UPLOAD_DIR = str(
    Path(tempfile.gettempdir()) / "basebot_uploads"
    if os.environ.get("VERCEL")
    else BACK_DIR / "uploads"
)

COMMUNITY_UPLOAD_DIR = os.path.join(UPLOAD_DIR, "community")
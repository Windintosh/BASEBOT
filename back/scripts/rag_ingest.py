import getpass
import hashlib
import os
import time
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


BACK_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BACK_DIR / "rag_data"
CHROMA_PATH = BACK_DIR / "chroma_db"


def main():
    files = sorted(DATA_PATH.glob("*.txt"))
    if not files:
        raise RuntimeError(f"색인할 문서가 없습니다: {DATA_PATH}")

    documents = []
    for path in files:
        content = path.read_text(encoding="utf-8-sig")
        if not content.strip():
            raise RuntimeError(f"빈 문서입니다: {path.name}")
        documents.append(
            Document(
                page_content=content,
                metadata={"source": path.name},
            )
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = splitter.split_documents(documents)
    if not chunks:
        raise RuntimeError("분할된 문서 조각이 없습니다.")

    ids = [
        hashlib.sha256(
            f"{chunk.metadata['source']}\0{i}\0{chunk.page_content}".encode()
        ).hexdigest()
        for i, chunk in enumerate(chunks)
    ]
    assert len(ids) == len(set(ids)), "문서 조각 ID가 중복됐습니다."

    print(f"원본 문서: {len(documents)}개 / 문서 조각: {len(chunks)}개")
    print(f"저장 위치: {CHROMA_PATH}")

    api_key = (
        os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or getpass.getpass("Gemini API 키 입력(화면에 표시되지 않음): ")
    )
    if not api_key.strip():
        raise RuntimeError("Gemini API 키가 필요합니다.")

    store = Chroma(
        collection_name="basebot",
        embedding_function=GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key,
        ),
        persist_directory=str(CHROMA_PATH),
    )

    existing_ids = set(store.get(include=[])["ids"])
    pending = [
        (doc_id, chunk)
        for doc_id, chunk in zip(ids, chunks)
        if doc_id not in existing_ids
    ]
    print(f"기존 조각: {len(existing_ids)}개 / 추가 대상: {len(pending)}개")

    for start in range(0, len(pending), 10):
        batch = pending[start:start + 10]
        store.add_documents(
            documents=[chunk for _, chunk in batch],
            ids=[doc_id for doc_id, _ in batch],
        )
        print(f"추가 완료: {min(start + 10, len(pending))}/{len(pending)}")
        time.sleep(15)

    saved_ids = set(store.get(include=[])["ids"])
    assert set(ids).issubset(saved_ids), "일부 문서 조각이 저장되지 않았습니다."
    print(f"색인 완료 / 현재 문서 조각 검증: {len(ids)}개")


if __name__ == "__main__":
    main()
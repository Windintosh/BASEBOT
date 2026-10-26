import os
import ssl

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

# 데이터베이스 연결 정보 설정(계정 및 비밀번호 제거)
DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
    query={"charset": "utf8mb4"},
)

connect_args = {}

if os.environ.get("DB_SSL_CA"):
    connect_args["ssl"] = ssl.create_default_context(
        cadata=os.environ["DB_SSL_CA"]
    )
elif os.environ.get("VERCEL"):
    raise RuntimeError("DB_SSL_CA is required on Vercel")

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,
    pool_size=2,
    max_overflow=0,
)


# Vercel에서는 환경변수로 Aiven에 연결
connect_args = {}

if os.environ.get("VERCEL") or os.environ.get("DB_HOST"):
    DATABASE_URL = URL.create(
        drivername="mysql+pymysql",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
        query={"charset": "utf8mb4"},
    )

    connect_args["ssl"] = ssl.create_default_context(
        cadata=os.environ["DB_SSL_CA"]
    )

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,
    pool_size=2,
    max_overflow=0,
)

# 세션 팩토리 생성
SessionFactory = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# 세션 생성
def get_session():
    with SessionFactory() as session:
        yield session

from sqlalchemy.orm import sessionmaker

# 기존에 SessionLocal이 없다면 선언
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI 의존성 주입(Depends)용 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
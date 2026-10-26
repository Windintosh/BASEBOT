import jwt

import os

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

# SECRET_KEY_OLD = os.environ["JWT_SECRET_KEY_OLD"]
SECRET_KEY = os.environ["JWT_SECRET_KEY"]

if len(SECRET_KEY.encode("utf-8")) < 32:
    raise RuntimeError("JWT_SECRET_KEY는 32바이트 이상이어야 합니다.")
ALGORITHM = "HS256"


# JWT 생성
def create_access_token(
        user_id: int,
        username: str,
role: str = "USER"
):
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# JWT 검증
def decode_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 만료되었습니다."
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 로그인 정보입니다."
        )
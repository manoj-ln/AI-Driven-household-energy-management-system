from fastapi import HTTPException, status


def verify_token(token: str) -> bool:
    if token != "secret-token":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    return True

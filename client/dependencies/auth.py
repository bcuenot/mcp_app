from fastapi import HTTPException

def extract_bearer_token(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Header Authorization manquant.",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Format Authorization invalide. Format attendu : Bearer <token>.",
        )

    return authorization.removeprefix("Bearer ").strip()
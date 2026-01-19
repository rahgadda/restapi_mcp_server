from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_env():
    return {"status": "ok"}
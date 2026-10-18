from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "online",
        "service": "RestroBot RAG Research Platform API",
        "version": "1.0.0"
    }

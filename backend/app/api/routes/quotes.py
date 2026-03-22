from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.email.quote_service import compare_quotes, generate_mock_quotes, ingest_quotes_for_rfp

router = APIRouter()


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/ingest-quotes/{rfp_id}")
def ingest_quotes(rfp_id: str, db: Session = Depends(get_db)) -> dict:
    return ingest_quotes_for_rfp(rfp_id=rfp_id, db=db)


@router.get("/compare-quotes/{rfp_id}")
def compare_quotes_endpoint(rfp_id: str, db: Session = Depends(get_db)) -> dict:
    return compare_quotes(rfp_id=rfp_id, db=db)


@router.post("/generate-mock-quotes/{rfp_id}")
def generate_mock_quotes_endpoint(rfp_id: str, db: Session = Depends(get_db)) -> dict:
    return generate_mock_quotes(rfp_id=rfp_id, db=db)

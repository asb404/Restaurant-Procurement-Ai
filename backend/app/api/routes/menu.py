from fastapi import APIRouter, Depends
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.input.pdf_ingestor import extract_text_from_pdf_url
from app.services.menu_processing import process_menu_text

router = APIRouter()


class ProcessMenuRequest(BaseModel):
    restaurant_name: str
    location: str
    raw_text: str | None = None
    menu_url: str | None = None
    pdf_url: str | None = None


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/process-menu")
def process_menu(payload: ProcessMenuRequest, db: Session = Depends(get_db)) -> dict:
    selected_text: str | None = None

    if payload.raw_text:
        selected_text = payload.raw_text
    elif payload.pdf_url:
        try:
            selected_text = extract_text_from_pdf_url(payload.pdf_url)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
    elif payload.menu_url:
        selected_text = payload.menu_url

    if not selected_text:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one input: raw_text, pdf_url, or menu_url",
        )

    return process_menu_text(
        restaurant_name=payload.restaurant_name,
        location=payload.location,
        text=selected_text,
        db_session=db,
    )

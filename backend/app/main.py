from fastapi import FastAPI

from app.api.routes.menu import router as menu_router
from app.api.routes.quotes import router as quotes_router
from app.db.base import Base
from app.db.session import engine

app = FastAPI()
app.include_router(menu_router)
app.include_router(quotes_router)

from dotenv import load_dotenv
load_dotenv()

@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "API is running"}

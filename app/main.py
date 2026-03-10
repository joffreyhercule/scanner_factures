import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

from app.config import BASE_DIR, IMAGES_DIR
from app.routers import clients, vehicles, invoices, upload
from app.database import db


@asynccontextmanager
async def lifespan(app):
    yield
    db.close()


app = FastAPI(title="Scanner Factures Garage", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients.router)
app.include_router(vehicles.router)
app.include_router(invoices.router)
app.include_router(upload.router)

app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")
app.mount("/", StaticFiles(directory=str(BASE_DIR / "frontend"), html=True), name="frontend")

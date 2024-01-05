from fastapi import FastAPI

import secrets
import validators
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import models,schemas
from .config import get_settings
from .database import SessionLocal, engine
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)

@app.get("/")
def read_root():
    return "Welcome to the URL shortener API :)"

@app.post("/url", response_model=schemas.URLCreateResponseBase)
def create_url(url: schemas.URLCreateRequestBase, db: Session = Depends(get_db)):
    if not validators.url(url.url):
        raise_bad_request(message="Your provided URL is not valid")
    print(url.url)

    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    key = "".join(secrets.choice(chars) for _ in range(8))
    #secret_key = "".join(secrets.choice(chars) for _ in range(10))
    db_url = models.URL(
        long_url=url.url, key=key, short_url=get_settings().base_url + "/" + key
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    db_url.url = key

    return db_url
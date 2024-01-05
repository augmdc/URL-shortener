import secrets
import validators
from fastapi import Depends, FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse

from fastapi.templating import Jinja2Templates
import os
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

# Directory where templates are stored
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

"""
Functions
"""
def process_url(long_url: str, db: Session):
    if not validators.url(long_url):
        return {"error": "Your provided URL is not valid"}

    existing_url = db.query(models.URL).filter(models.URL.long_url == long_url).first()
    if existing_url:
        return {"short_url": existing_url.short_url, "url_key": existing_url.key}

    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    key = "".join(secrets.choice(chars) for _ in range(8))
    short_url = get_settings().base_url + "/" + key

    db_url = models.URL(
        long_url=long_url,
        key=key, short_url=short_url
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    return {"short_url": db_url.short_url, "url_key": db_url.key}


def raise_not_found(request):
    message = f"URL '{request.url}' doesn't exist"
    raise HTTPException(status_code=404, detail=message)

def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)

"""
GUI Endpoints
"""
@app.get("/gui")
def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/gui/url", response_class=HTMLResponse)
def create_url_gui(request: Request, long_url: str = Form(...), db: Session = Depends(get_db)):
    result = process_url(long_url, db)
    if "error" in result:
        return templates.TemplateResponse("index.html", {"request": request, "error": result["error"]})

    return templates.TemplateResponse("index.html", {
        "request": request, 
        "short_url": result["short_url"], 
        "url_key": result["url_key"]
    })


"""
API Endpoints
"""
@app.get("/api/{url_key}")
def forward_to_target_url(
        url_key: str,
        request: Request,
        db: Session = Depends(get_db)
    ):
    db_url = (
        db.query(models.URL)
        .filter(models.URL.key == url_key)
        .first()
    )
    if db_url:
        return RedirectResponse(status_code=302, url=db_url.long_url)
    else:
        raise_not_found(request)

@app.post("/api/url", response_model=schemas.URLCreateResponseBase)
def create_url_api(url: schemas.URLCreateRequestBase, db: Session = Depends(get_db)):
    result = process_url(url.url, db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.delete("/api/{url_key}")
def delete_url(url_key: str, db: Session = Depends(get_db)):
    # Query the database for the URL
    db_url = db.query(models.URL).filter(models.URL.key == url_key).first()

    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    else:
        # Delete the URL
        db.delete(db_url)
        db.commit()

        raise HTTPException(status_code=200)
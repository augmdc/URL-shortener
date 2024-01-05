from pydantic import BaseModel

class URLCreateRequestBase(BaseModel):
    url: str

class URLCreateResponseBase(BaseModel):
    key: str
    long_url: str
    short_url: str

    class Config:
        orm_mode = True

class URLCreateResponseLocation(BaseModel):
    location: str
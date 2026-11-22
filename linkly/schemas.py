from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class LinkCreate(BaseModel):
    url: HttpUrl


class LinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    target_url: str
    created_at: datetime

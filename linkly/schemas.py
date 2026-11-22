from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class LinkCreate(BaseModel):
    url: HttpUrl


class LinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    target_url: str
    created_at: datetime


class DailyClickCount(BaseModel):
    date: date
    count: int


class ReferrerClickCount(BaseModel):
    referrer: str
    count: int


class LinkStats(BaseModel):
    total_clicks: int
    clicks_per_day: list[DailyClickCount]
    top_referrers: list[ReferrerClickCount]

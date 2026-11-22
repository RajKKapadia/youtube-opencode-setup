import secrets
import string
from datetime import UTC, date, datetime, time, timedelta

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from linkly.db import get_db
from linkly.models import Click, Link
from linkly.schemas import LinkCreate, LinkOut, LinkStats

CODE_ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6

app = FastAPI(title="linkly")


def _generate_code(db: Session) -> str:
    while True:
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
        if db.scalar(select(Link.id).where(Link.code == code)) is None:
            return code


def _get_link_or_404(db: Session, code: str) -> Link:
    link = db.scalar(select(Link).where(Link.code == code))
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


@app.post("/links", response_model=LinkOut, status_code=status.HTTP_201_CREATED)
def create_link(payload: LinkCreate, db: Session = Depends(get_db)) -> Link:
    link = Link(code=_generate_code(db), target_url=str(payload.url))
    db.add(link)
    db.commit()
    return link


@app.get("/links/{code}", response_model=LinkOut)
def get_link(code: str, db: Session = Depends(get_db)) -> Link:
    return _get_link_or_404(db, code)


@app.get("/links/{code}/stats", response_model=LinkStats)
def get_link_stats(code: str, db: Session = Depends(get_db)) -> LinkStats:
    link = _get_link_or_404(db, code)
    now = datetime.now(UTC)
    first_day = now.date() - timedelta(days=6)
    start_of_period = datetime.combine(first_day, time.min, tzinfo=UTC)

    total_clicks = db.scalar(
        select(func.count(Click.id)).where(Click.link_id == link.id)
    ) or 0
    daily_counts = db.execute(
        select(func.date(Click.timestamp), func.count(Click.id))
        .where(
            Click.link_id == link.id,
            Click.timestamp >= start_of_period,
            Click.timestamp <= now,
        )
        .group_by(func.date(Click.timestamp))
    ).all()
    counts_by_day = {date.fromisoformat(day): count for day, count in daily_counts}

    referrer_counts = db.execute(
        select(Click.referrer, func.count(Click.id))
        .where(Click.link_id == link.id, Click.referrer.is_not(None))
        .group_by(Click.referrer)
        .order_by(func.count(Click.id).desc(), Click.referrer.asc())
        .limit(5)
    ).all()

    return LinkStats(
        total_clicks=total_clicks,
        clicks_per_day=[
            {
                "date": first_day + timedelta(days=offset),
                "count": counts_by_day.get(first_day + timedelta(days=offset), 0),
            }
            for offset in range(7)
        ],
        top_referrers=[
            {"referrer": referrer, "count": count}
            for referrer, count in referrer_counts
        ],
    )


@app.get("/{code}")
def redirect(
    code: str, request: Request, db: Session = Depends(get_db)
) -> RedirectResponse:
    link = _get_link_or_404(db, code)
    db.add(
        Click(
            link_id=link.id,
            timestamp=datetime.now(UTC),
            referrer=request.headers.get("referer"),
            user_agent=request.headers.get("user-agent"),
        )
    )
    db.commit()
    return RedirectResponse(
        link.target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )

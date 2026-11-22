import secrets
import string

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from linkly.db import get_db
from linkly.models import Link
from linkly.schemas import LinkCreate, LinkOut

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


@app.get("/{code}")
def redirect(code: str, db: Session = Depends(get_db)) -> RedirectResponse:
    link = _get_link_or_404(db, code)
    return RedirectResponse(link.target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/votes", tags=["Votos"])


@router.post("", response_model=schemas.VoteOut, status_code=status.HTTP_201_CREATED)
def cast_vote(data: schemas.VoteCreate, db: Session = Depends(get_db)):
    voter = db.get(models.Voter, data.voter_id)
    if not voter:
        raise HTTPException(404, "Votante no encontrado")

    candidate = db.get(models.Candidate, data.candidate_id)
    if not candidate:
        raise HTTPException(404, "El candidate_id no es válido")

    if voter.has_voted:
        raise HTTPException(409, "Este votante ya emitió su voto")

    vote = models.Vote(voter_id=voter.id, candidate_id=candidate.id)
    voter.has_voted = True       # integridad: marcar al votante
    candidate.votes += 1         # integridad: sumar al candidato
    db.add(vote)

    try:
        db.commit()              # las 3 operaciones se guardan juntas o ninguna
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Este votante ya emitió su voto")

    db.refresh(vote)
    return vote


@router.get("", response_model=List[schemas.VoteOut])
def list_votes(db: Session = Depends(get_db)):
    return db.query(models.Vote).order_by(models.Vote.id).all()


@router.get("/statistics", response_model=schemas.Statistics)
def statistics(db: Session = Depends(get_db)):
    candidates = db.query(models.Candidate).order_by(models.Candidate.id).all()
    total_votes = db.query(models.Vote).count()
    voters_voted = db.query(models.Voter).filter(models.Voter.has_voted.is_(True)).count()

    stats = [
        schemas.CandidateStats(
            candidate_id=c.id,
            name=c.name,
            party=c.party,
            total_votes=c.votes,
            percentage=round(c.votes * 100 / total_votes, 2) if total_votes else 0.0,
        )
        for c in candidates
    ]
    return schemas.Statistics(
        total_votes=total_votes,
        total_voters_who_voted=voters_voted,
        candidates=stats,
    )

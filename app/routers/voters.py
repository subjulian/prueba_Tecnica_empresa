from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/voters", tags=["Votantes"])


@router.post("", response_model=schemas.VoterOut, status_code=status.HTTP_201_CREATED)
def create_voter(data: schemas.VoterCreate, db: Session = Depends(get_db)):
    name = data.name.strip()

    # Restricción: un votante no puede ser candidato
    if db.query(models.Candidate).filter(
        func.lower(models.Candidate.name) == name.lower()
    ).first():
        raise HTTPException(409, "Esta persona ya está registrada como candidato")

    if db.query(models.Voter).filter(models.Voter.email == data.email).first():
        raise HTTPException(409, "Ya existe un votante con ese correo")

    voter = models.Voter(name=name, email=data.email)
    db.add(voter)
    db.commit()
    db.refresh(voter)
    return voter


@router.get("", response_model=List[schemas.VoterOut])
def list_voters(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    has_voted: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.Voter)
    if name:
        q = q.filter(models.Voter.name.ilike(f"%{name}%"))
    if has_voted is not None:
        q = q.filter(models.Voter.has_voted == has_voted)
    return q.order_by(models.Voter.id).offset(skip).limit(limit).all()


@router.get("/{voter_id}", response_model=schemas.VoterOut)
def get_voter(voter_id: int, db: Session = Depends(get_db)):
    voter = db.get(models.Voter, voter_id)
    if not voter:
        raise HTTPException(404, "Votante no encontrado")
    return voter


@router.delete("/{voter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_voter(voter_id: int, db: Session = Depends(get_db)):
    voter = db.get(models.Voter, voter_id)
    if not voter:
        raise HTTPException(404, "Votante no encontrado")

    # Si ya votó, se elimina su voto y se descuenta del candidato
    # para que las estadísticas sigan siendo correctas
    vote = db.query(models.Vote).filter(models.Vote.voter_id == voter_id).first()
    if vote:
        candidate = db.get(models.Candidate, vote.candidate_id)
        if candidate and candidate.votes > 0:
            candidate.votes -= 1
        db.delete(vote)

    db.delete(voter)
    db.commit()

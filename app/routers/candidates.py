from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/candidates", tags=["Candidatos"])


@router.post("", response_model=schemas.CandidateOut, status_code=status.HTTP_201_CREATED)
def create_candidate(data: schemas.CandidateCreate, db: Session = Depends(get_db)):
    name = data.name.strip()

    # Restricción: un candidato no puede ser votante
    if db.query(models.Voter).filter(
        func.lower(models.Voter.name) == name.lower()
    ).first():
        raise HTTPException(409, "Esta persona ya está registrada como votante")

    if db.query(models.Candidate).filter(
        func.lower(models.Candidate.name) == name.lower()
    ).first():
        raise HTTPException(409, "Ya existe un candidato con ese nombre")

    candidate = models.Candidate(name=name, party=data.party)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.get("", response_model=List[schemas.CandidateOut])
def list_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    party: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.Candidate)
    if name:
        q = q.filter(models.Candidate.name.ilike(f"%{name}%"))
    if party:
        q = q.filter(models.Candidate.party.ilike(f"%{party}%"))
    return q.order_by(models.Candidate.id).offset(skip).limit(limit).all()


@router.get("/{candidate_id}", response_model=schemas.CandidateOut)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(models.Candidate, candidate_id)
    if not candidate:
        raise HTTPException(404, "Candidato no encontrado")
    return candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(models.Candidate, candidate_id)
    if not candidate:
        raise HTTPException(404, "Candidato no encontrado")
    if candidate.votes > 0:
        raise HTTPException(409, "No se puede eliminar un candidato que ya tiene votos")
    db.delete(candidate)
    db.commit()

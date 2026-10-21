from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class VoterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class VoterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    has_voted: bool


class CandidateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    party: Optional[str] = Field(None, max_length=100)


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    party: Optional[str]
    votes: int


class VoteCreate(BaseModel):
    voter_id: int
    candidate_id: int


class VoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    voter_id: int
    candidate_id: int


class CandidateStats(BaseModel):
    candidate_id: int
    name: str
    party: Optional[str]
    total_votes: int
    percentage: float


class Statistics(BaseModel):
    total_votes: int
    total_voters_who_voted: int
    candidates: List[CandidateStats]

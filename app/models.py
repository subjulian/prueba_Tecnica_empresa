from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Voter(Base):
    __tablename__ = "voters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    has_voted = Column(Boolean, default=False, nullable=False)

    vote = relationship("Vote", back_populates="voter", uselist=False)


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    party = Column(String(100), nullable=True)
    votes = Column(Integer, default=0, nullable=False)

    received_votes = relationship("Vote", back_populates="candidate")


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    # unique=True: la propia BD garantiza un solo voto por votante
    voter_id = Column(Integer, ForeignKey("voters.id"), unique=True, nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)

    voter = relationship("Voter", back_populates="vote")
    candidate = relationship("Candidate", back_populates="received_votes")

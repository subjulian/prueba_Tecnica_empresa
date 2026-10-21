from fastapi import FastAPI

from .database import Base, engine
from .routers import candidates, voters, votes

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Votaciones",
    description="Prueba técnica: gestión de votantes, candidatos y votos.",
    version="1.0.0",
)

app.include_router(voters.router)
app.include_router(candidates.router)
app.include_router(votes.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "API de Votaciones funcionando. Documentación en /docs"}

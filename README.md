# API de Votaciones

API REST (FastAPI + SQLAlchemy) para gestionar votantes, candidatos y votos.

## Ejecución rápida
- **Windows:** doble clic en `run.bat`
- **Linux / Mac:** `./run.sh`

Crea el entorno virtual, instala dependencias y levanta el servidor.
Swagger: http://localhost:8000/docs

## Ejecución manual
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Base de datos
SQLite por defecto (`votaciones.db`, se crea sola). Para PostgreSQL/MySQL:
```bash
export DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/votaciones"
```

## Endpoints
- Votantes: `POST/GET /voters`, `GET/DELETE /voters/{id}`
- Candidatos: `POST/GET /candidates`, `GET/DELETE /candidates/{id}`
- Votos: `POST/GET /votes`, `GET /votes/statistics`
- Filtros y paginación: `skip`, `limit`, `name`, `has_voted` (votantes), `party` (candidatos)

## Reglas
- Un votante no puede ser candidato (ni viceversa; se compara por nombre).
- Un voto por votante (validación + restricción UNIQUE en BD).
- Al votar: `has_voted = true` y `votes + 1` en una sola transacción.
- Eliminar votante con voto: se borra el voto y se descuenta al candidato.
- No se puede eliminar un candidato con votos.

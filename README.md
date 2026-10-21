# API de Votaciones

API REST desarrollada con **FastAPI + SQLAlchemy** para gestionar votantes, candidatos y votos, con estadísticas de la votación.

- Lenguaje: Python 3.9+
- Base de datos: SQLite por defecto (se crea sola). Compatible con PostgreSQL y MySQL.
- Documentación interactiva: Swagger en `/docs`

## Estructura

```
votaciones/
├── app/
│   ├── main.py          # Punto de entrada
│   ├── database.py      # Conexión a la BD
│   ├── models.py        # Tablas (Voter, Candidate, Vote)
│   ├── schemas.py       # Validación de entrada/salida (Pydantic)
│   └── routers/         # Endpoints: voters, candidates, votes
├── docs/images/         # Capturas usadas en este README
├── requirements.txt
├── run.bat / run.sh     # Ejecución rápida
└── README.md
```

## 1. Ejecutar el proyecto localmente

### Opción rápida
- **Windows:** doble clic en `run.bat`
- **Linux / Mac:** `./run.sh`

### Opción manual

**Windows (PowerShell)**
```powershell
py -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Linux / Mac**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Cuando aparezca `Uvicorn running on http://127.0.0.1:8000`, abre:

- Swagger: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

### Usar PostgreSQL o MySQL (opcional)
```bash
# PostgreSQL
export DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/votaciones"
# MySQL
export DATABASE_URL="mysql+pymysql://user:pass@localhost:3306/votaciones"
```
(Instalar antes el driver: `pip install psycopg2-binary` o `pip install pymysql`.)

## 2. Endpoints

| Recurso | Método y ruta | Descripción |
|---|---|---|
| Votantes | `POST /voters` | Registrar votante |
| | `GET /voters` | Listar (filtros: `skip`, `limit`, `name`, `has_voted`) |
| | `GET /voters/{id}` | Detalle |
| | `DELETE /voters/{id}` | Eliminar |
| Candidatos | `POST /candidates` | Registrar candidato |
| | `GET /candidates` | Listar (filtros: `skip`, `limit`, `name`, `party`) |
| | `GET /candidates/{id}` | Detalle |
| | `DELETE /candidates/{id}` | Eliminar |
| Votos | `POST /votes` | Emitir voto |
| | `GET /votes` | Listar votos |
| | `GET /votes/statistics` | Estadísticas |

![Endpoints en Swagger](docs/images/01-swagger-endpoints.png)

## 3. Ejemplos de uso

### Con curl

> En Windows PowerShell usa `curl.exe` (no `curl`) y comillas dobles escapadas, o usa los ejemplos con `Invoke-RestMethod` más abajo.

```bash
# Crear votante
curl -X POST http://127.0.0.1:8000/voters \
  -H "Content-Type: application/json" \
  -d '{"name": "rodolfo", "email": "user12@example.com"}'

# Crear candidato
curl -X POST http://127.0.0.1:8000/candidates \
  -H "Content-Type: application/json" \
  -d '{"name": "emilio", "party": "rojo"}'

# Emitir voto
curl -X POST http://127.0.0.1:8000/votes \
  -H "Content-Type: application/json" \
  -d '{"voter_id": 1, "candidate_id": 1}'

# Listar con paginación y filtro
curl "http://127.0.0.1:8000/voters?skip=0&limit=10&has_voted=false"

# Estadísticas
curl http://127.0.0.1:8000/votes/statistics
```

### Con PowerShell (Windows)

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/voters `
  -ContentType "application/json" `
  -Body '{"name":"rodolfo","email":"user12@example.com"}'

Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/candidates `
  -ContentType "application/json" `
  -Body '{"name":"emilio","party":"rojo"}'

Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/votes `
  -ContentType "application/json" `
  -Body '{"voter_id":1,"candidate_id":1}'

Invoke-RestMethod http://127.0.0.1:8000/votes/statistics
```


### Con Swagger (`/docs`)

Abre el endpoint, pulsa **Try it out**, edita el JSON y pulsa **Execute**.

**Crear un votante (request):**

![Request crear votante](docs/images/02-crear-votante-request.png)

**Respuesta `201 Created`:**

![Respuesta 201](docs/images/03-crear-votante-201.png)

**Listar votantes (`GET /voters`):**

![Listar votantes](docs/images/04-listar-votantes.png)

**Listar candidatos (`GET /candidates`):** el candidato muestra su conteo de `votes` actualizado.

![Listar candidatos](docs/images/05-listar-candidatos.png)

**El votante queda marcado con `has_voted: true` tras votar:**

![has_voted true](docs/images/07-has-voted-true.png)

## 4. Estadísticas de la votación

`GET /votes/statistics` devuelve el total de votos por candidato, el porcentaje de cada uno y el total de votantes que han votado.

Ejemplo de respuesta (con los datos de las capturas: un voto para `emilio`):

```json
{
  "total_votes": 1,
  "total_voters_who_voted": 1,
  "candidates": [
    {
      "candidate_id": 1,
      "name": "emilio",
      "party": "rojo",
      "total_votes": 1,
      "percentage": 100.0
    }
  ]
}
```

![Estadísticas](docs/images/estadisticas.png)

## 5. Validaciones y manejo de errores

| Situación | Código |
|---|---|
| Datos inválidos (correo mal formado, nombre vacío) | `422` |
| Votante / candidato / `candidate_id` inexistente | `404` |
| Correo repetido | `409` |
| Votante registrado como candidato (o viceversa, se compara por nombre) | `409` |
| Votante que ya votó | `409` |
| Eliminar candidato que ya tiene votos | `409` |

**Ejemplo: intentar votar dos veces**

![Error 409](docs/images/06-error-409-ya-voto.png)

## 6. Decisiones de diseño

- **Un voto por votante:** se valida en el código y además `Vote.voter_id` es `UNIQUE` en la base de datos.
- **Integridad:** al votar se crea el voto, se marca `has_voted = true` y se suma `+1` al candidato en **una sola transacción**.
- **Borrar un votante que ya votó:** se elimina también su voto y se descuenta del candidato, para que las estadísticas sigan siendo correctas.
- **Borrar un candidato con votos:** se bloquea para no perder votos emitidos.
- **Paginación y filtros** en las listas de votantes y candidatos (extra opcional).

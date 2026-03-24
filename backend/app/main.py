from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings
from app.db.connection import get_connection, get_connection_string_masked
from app.schemas.attempt_schema import AttemptEvaluationRequest
from app.schemas.attempt_submit_schema import AttemptSubmitRequest
from app.schemas.term_schema import TermValidationRequest
from app.schemas.user_state_schema import UserDayStateRequest
from app.services.attempt_evaluation_service import evaluate_attempt
from app.services.attempt_submit_service import submit_attempt
from app.services.day_state_service import get_day_state
from app.services.debug_target_service import get_debug_target
from app.services.term_validation_service import validate_term
from app.services.user_day_state_service import get_user_day_state

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5178",
        "http://localhost:5178"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/db-health")
def db_health() -> dict:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT @@SERVERNAME AS DES_SERVIDOR, DB_NAME() AS DES_BASE_DATOS")
        row = cursor.fetchone()

        return {
            "status": "ok",
            "server": row.DES_SERVIDOR,
            "database": row.DES_BASE_DATOS,
            "connection": get_connection_string_masked(),
        }
    finally:
        conn.close()


@app.get("/day-state")
def day_state() -> dict:
    return get_day_state()


@app.get("/debug-target")
def debug_target() -> dict:
    return get_debug_target()


@app.post("/term-validation")
def term_validation(payload: TermValidationRequest) -> dict:
    return validate_term(payload.cod_termino)


@app.post("/attempt-evaluation")
def attempt_evaluation(payload: AttemptEvaluationRequest) -> dict:
    return evaluate_attempt(payload.cod_termino)


@app.post("/attempt-submit")
def attempt_submit(payload: AttemptSubmitRequest) -> dict:
    return submit_attempt(
        cod_usuario=payload.cod_usuario,
        des_usuario=payload.des_usuario,
        cod_termino=payload.cod_termino
    )


@app.post("/user-day-state")
def user_day_state(payload: UserDayStateRequest) -> dict:
    return get_user_day_state(payload.cod_usuario)
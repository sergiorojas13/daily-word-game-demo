from pydantic import BaseModel, Field


class AttemptEvaluationRequest(BaseModel):
    cod_termino: str = Field(..., min_length=1, max_length=32)


class AttemptEvaluationResponse(BaseModel):
    status: str
    data: dict

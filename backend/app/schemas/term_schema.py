from pydantic import BaseModel, Field


class TermValidationRequest(BaseModel):
    cod_termino: str = Field(..., min_length=1, max_length=32)


class TermValidationResponse(BaseModel):
    status: str
    data: dict

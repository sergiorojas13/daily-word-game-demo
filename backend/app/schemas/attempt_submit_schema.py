from pydantic import BaseModel, Field


class AttemptSubmitRequest(BaseModel):
    cod_usuario: str = Field(..., min_length=1, max_length=128)
    des_usuario: str | None = Field(default=None, max_length=256)
    cod_termino: str = Field(..., min_length=1, max_length=32)

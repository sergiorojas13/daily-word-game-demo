from pydantic import BaseModel, Field


class UserDayStateRequest(BaseModel):
    cod_usuario: str = Field(..., min_length=1, max_length=128)

from pydantic import BaseModel, field_validator


class RequestPlan(BaseModel):
    name: str
    duration: str
    rate_of_return: float
    status: str = 'active'
    minimum: int
    maximum: int

    @field_validator("minimum")
    @classmethod
    def not_less_than_zero(cls, value):
        if value <= 0:
            raise ValueError("Cannot be less than zero")
        return value


class ResponsePlan(BaseModel):
    name: str
    duration: str
    rate_of_return: float
    status: str = 'active'
    minimum: int
    maximum: int
    amount_to_receive:str 

class ListResponsePlan(BaseModel):
    plans:list[ResponsePlan]


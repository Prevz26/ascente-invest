from pydantic import BaseModel, field_validator, model_validator, EmailStr
from typing import Literal
from pydantic import ValidationError

class RegistrationSchema(BaseModel):
    username: str
    fullname: str
    email: EmailStr
    password: str
    confirm_password: str
    is_admin: bool = False
    country: Literal[
        'united states', 'canada', 'united kingdom', 'australia', 'india', 'germany', 'france', 'italy', 'spain', 'mexico',
        'brazil', 'south korea', 'japan', 'china', 'russia', 'south africa', 'nigeria', 'argentina', 'egypt', 'saudi arabia',
        'sweden', 'norway', 'netherlands', 'denmark', 'finland', 'belgium', 'switzerland', 'austria', 'poland', 'portugal'
    ]


    
    @field_validator("*", mode="before")
    @classmethod
    def lowercase_fields(cls, v: str, info) -> str:
        if info.field_name != "password" and isinstance(v, str):
            return v.lower()
        return v


    @model_validator(mode="after")
    @classmethod
    def check_password(cls, values):
        if values.password != values.confirm_password:
            raise ValueError("password does not match")
        return values 
    
    @field_validator("username", "fullname", "email", "country")
    @classmethod
    def validate_not_empty(cls, value):
        if not value.strip():
            raise ValueError("field cannot be empty")
        return value
    
    @field_validator("password")
    @classmethod
    def verify_passowrd(cls, value):
        if len(value) < 8:
            raise ValueError("password is less than 8 characters")
        return value 



    

class LoginSchema(BaseModel):
    username:str
    password:str  

    @field_validator("username", "password")
    @classmethod
    def validate_not_empty(cls, value):
        if not value.strip():
            raise ValueError("fields cannot be empty")
        return value


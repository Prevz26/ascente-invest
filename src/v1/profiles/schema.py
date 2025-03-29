from pydantic import BaseModel, Field
from typing import Optional

class ProfileSchema(BaseModel):
    first_name: Optional[str] = Field(None, description="The user's first name")
    last_name: Optional[str] = Field(None, description="The user's last name")
    date_of_birth: Optional[str] = Field(None, description="The user's date of birth")
    bio: Optional[str] = Field(None, description="The user's bio")
    country: Optional[str] = Field(None, description="The user's country")
    city: Optional[str] = Field(None, description="The user's city")
    address: Optional[str] = Field(None, description="The user's address")
    created_at: Optional[str] = Field(None, description="The user's creation date")
    updated_at: Optional[str] = Field(None, description="The user's last update date")

    class Config:
        orm_mode = True


class ProfileReadSchema(ProfileSchema):
    email: str = Field(..., description="The user's email", read_only=True)

    class Config(ProfileSchema.Config):
        read_only_fields = ["fist_name", "created_at", "updated_at"]


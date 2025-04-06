import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

class DumpProfileSchema(BaseModel):
    username: str = Field(max_length=50)
    fullname: str = Field(max_length=100)
    email: EmailStr = Field(max_length=100)
    referral_id: Optional[str] = Field(max_length=50, default=None)
    first_name: Optional[str] = Field(max_length=30, default=None)
    last_name: Optional[str] = Field(max_length=30, default=None)
    date_of_birth: Optional[datetime.date] = None
    bio: Optional[str] = None
    country: Literal[
        'united states', 'canada', 'united kingdom', 'australia', 'india', 'germany', 'france', 'italy', 'spain', 'mexico',
        'brazil', 'south korea', 'japan', 'china', 'russia', 'south africa', 'nigeria', 'argentina', 'egypt', 'saudi arabia',
        'sweden', 'norway', 'netherlands', 'denmark', 'finland', 'belgium', 'switzerland', 'austria', 'poland', 'portugal'
    ]
    city: Optional[str] = Field(max_length=50, default=None)
    address: Optional[str] = Field(max_length=255, default=None)
    is_admin: bool = False
    is_fully_registered: bool = False
    mobile_number: Optional[str] = Field(max_length=20, default=None)
    street1: Optional[str] = Field(max_length=255, default=None)
    street2: Optional[str] = Field(max_length=255, default=None)
    state: Optional[str] = Field(max_length=50, default=None)
    zip_code: Optional[str] = Field(max_length=20, default=None)
    emergency_contact_name: Optional[str] = Field(max_length=100, default=None)
    emergency_contact_number: Optional[str] = Field(max_length=20, default=None)
    preferred_contact_method: Optional[str] = Field(max_length=20, default=None)


import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

class LoadProfileSchema(BaseModel):
    username: Optional[str] = Field(max_length=50, default=None)
    fullname: Optional[str] = Field(max_length=100, default=None)
    email: Optional[EmailStr] = Field(max_length=100, default=None)
    country: Optional[Literal[
        'united states', 'canada', 'united kingdom', 'australia', 'india', 'germany', 'france', 'italy', 'spain', 'mexico',
        'brazil', 'south korea', 'japan', 'china', 'russia', 'south africa', 'nigeria', 'argentina', 'egypt', 'saudi arabia',
        'sweden', 'norway', 'netherlands', 'denmark', 'finland', 'belgium', 'switzerland', 'austria', 'poland', 'portugal'
    ]] = None
    referral_id: Optional[str] = Field(max_length=50, default=None)
    first_name: Optional[str] = Field(max_length=30, default=None)
    last_name: Optional[str] = Field(max_length=30, default=None)
    date_of_birth: Optional[datetime.date] = None
    bio: Optional[str] = None
    city: Optional[str] = Field(max_length=50, default=None)
    address: Optional[str] = Field(max_length=255, default=None)
    is_admin: bool = False
    is_fully_registered: bool = False
    mobile_number: Optional[str] = Field(max_length=20, default=None)
    street1: Optional[str] = Field(max_length=255, default=None)
    street2: Optional[str] = Field(max_length=255, default=None)
    state: Optional[str] = Field(max_length=50, default=None)
    zip_code: Optional[str] = Field(max_length=20, default=None)
    emergency_contact_name: Optional[str] = Field(max_length=100, default=None)
    emergency_contact_number: Optional[str] = Field(max_length=20, default=None)
    preferred_contact_method: Optional[str] = Field(max_length=20, default=None)


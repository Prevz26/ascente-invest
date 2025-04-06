from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from base.model import BaseModel


class User(BaseModel):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    fullname = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    referral_id = Column(String(50), nullable=True)
    first_name = Column(String(30), nullable=True)
    last_name = Column(String(30), nullable=True)
    date_of_birth = Column(TIMESTAMP(timezone=False), nullable=True)
    bio = Column(String, nullable=True)
    country = Column(String(50), nullable=True)
    city = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_fully_registered = Column(Boolean, default=False, nullable=False)
    mobile_number = Column(String(20), nullable=True)
    street1 = Column(String(255), nullable=True)
    street2 = Column(String(255), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(20), nullable=True)
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_number = Column(String(20), nullable=True)
    preferred_contact_method = Column(String(20), nullable=True)


    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'fullname': self.fullname,
            'email': self.email,
            'referral_id': self.referral_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': str(self.date_of_birth) if self.date_of_birth else None,
            'bio': self.bio,
            'country': self.country,
            'city': self.city,
            'address': self.address,
            'is_admin': self.is_admin
        }

    def __repr__(self):
        return f"<User {self.username}>"


class RefreshToken(BaseModel):
    __tablename__ = 'refresh_token'

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    revoked = Column(Boolean, nullable=True)
    expires_at = Column(TIMESTAMP(timezone=False), nullable=True)


#when models are in the different module, in the relationship func, use the backref argument rather than bacl_populate to prevent import errors 
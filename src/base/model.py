import uuid
from utils.dependency import db
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy as sa 

class BaseModel(db.Model):
    __abstract__ = True
    unique_id = sa.Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())





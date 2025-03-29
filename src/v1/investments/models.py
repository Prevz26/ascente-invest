from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from base.model import BaseModel

class Investments(BaseModel):
    __tablename__ = 'investments'
    id = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False)
    expected_return = Column(Integer, nullable=False)
    
    invested_date = Column(DateTime, nullable=True)
    expected_date = Column(DateTime, nullable=True)
    last_viewed = Column(DateTime, nullable=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='investments')

    wallet_id = Column(Integer, ForeignKey('wallets.id'))
    wallets = relationship('Wallet', back_populates='investments')

    plan_id = Column(Integer, ForeignKey('plans.id'))
    plan = relationship('Plans', back_populates='investments')

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'expected_return': self.expected_return,
            'invested_date': self.invested_date.isoformat() if self.invested_date else None,
            'expected_date': self.expected_date.isoformat() if self.expected_date else None,
            'last_viewed': self.last_viewed.isoformat() if self.last_viewed else None,
            'user_id': self.user_id,
            'wallet_id': self.wallet_id,
            'plan_id': self.plan_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Investment(id={self.id}, amount={self.amount}, expected_return={self.expected_return}, invested_date={self.invested_date})>'

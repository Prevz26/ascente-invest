from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from base.model import BaseModel
from sqlalchemy.ext.hybrid import hybrid_property

class Investments(BaseModel):
    __tablename__ = 'investments'
    id = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False)
    
    invested_date = Column(DateTime, nullable=True)
    last_viewed = Column(DateTime, nullable=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', backref='investments')

    wallet_id = Column(Integer, ForeignKey('wallets.id'))
    wallet = relationship('Wallet', backref='investments')

    plan_id = Column(Integer, ForeignKey('plans.id'))
    plan = relationship('Plans', backref='investments')

    @hybrid_property
    def maturity_date(self):
        """Calculate the investment maturity date"""
        return self.invested_date + self.plan.duration #use the time parser to convert this to datetime to get the accurate date

    @hybrid_property
    def profit(self):
        """Calculate profit"""
        return (self.amount * self.plan.rate_of_return)

    @hybrid_property
    def total_payout(self):
        """Calculate total payout (Investment + Profit)"""
        return self.amount + self.profit
    

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

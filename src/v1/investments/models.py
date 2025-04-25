from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from base.model import BaseModel
from sqlalchemy.ext.hybrid import hybrid_property
import parsedatetime
import datetime

class Investments(BaseModel):
    __tablename__ = 'investments'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    amount = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default='active')
    invested_date = Column(DateTime, nullable=True)
    last_viewed = Column(DateTime, nullable=True)
    profit_added = Column(DateTime, nullable=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', backref='investments')

    wallet_id = Column(Integer, ForeignKey('wallets.id'))
    wallet = relationship('Wallet', backref='investments')

    plan_id = Column(Integer, ForeignKey('plans.id'))
    plan = relationship('Plan', backref='investments')
    is_active = Column(Boolean, default=False)

    @hybrid_property
    def maturity_date(self):
        """Calculate the investment maturity date"""
        if not self.invested_date or not self.plan.duration:
            return None
            
        cal = parsedatetime.Calendar()
        duration_str = self.plan.duration
        if not duration_str.lower().startswith("in "):
            duration_str = "in " + duration_str.strip()
            
        time_struct, status = cal.parse(duration_str, self.invested_date.timetuple())
        if status == 1:
            maturity_date = datetime.datetime(*time_struct[:6])
            return {
                "maturity date": maturity_date.strftime("%d/%m/%Y"), 
                "date": maturity_date
                }
        else:
            raise ValueError("Could not parse duration")

    @hybrid_property
    def is_matured(self):
        """Check if investment is matured"""
        if not self.maturity_date:
            return False
        return datetime.datetime.now() >= self.maturity_date

    @hybrid_property
    def profit(self):
        """Calculate profit"""
        get_profit = self.amount * self.plan.rate_of_return
        return get_profit

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

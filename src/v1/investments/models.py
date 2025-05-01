from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship
from base.model import BaseModel
from sqlalchemy.ext.hybrid import hybrid_property
import parsedatetime
import datetime

class Investments(BaseModel):
    __tablename__ = 'investments'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    amount = Column(Numeric(10,2), nullable=False)
    status = Column(String(20), nullable=False, default='active')
    invested_date = Column(DateTime, nullable=True)
    last_viewed = Column(DateTime, nullable=True)
    profit_added = Column(Numeric(10,2), nullable=True)
    date_profit_added = Column(DateTime, nullable=True)
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
        maturity_date = self.maturity_date["date"]
        return datetime.datetime.now() >= maturity_date

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
        maturity = self.maturity_date
        return {
            'id': self.id,
            'amount': self.amount,
            'status': self.status,
            'invested_date': self.invested_date.isoformat() if self.invested_date else None,
            'last_viewed': self.last_viewed.isoformat() if self.last_viewed else None,
            'profit_added': self.profit_added if self.profit_added else None,
            'date_profit_added': self.date_profit_added.isoformat() if self.date_profit_added else None,
            'user_id': self.user_id,
            'wallet_id': self.wallet_id,
            'plan_id': self.plan_id,
            'is_active': self.is_active,
            'profit': self.profit,
            'total_payout': self.total_payout,
            'maturity_date': maturity["maturity date"] if maturity else None,
            'maturity_date_obj': maturity["date"].isoformat() if maturity else None,
            'is_matured': self.is_matured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'plan': {
                'name': self.plan.name if self.plan else None,
                'rate_of_return': self.plan.rate_of_return if self.plan else None, 
                "duration": self.plan.duration if self.plan else None,
            },
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Investment(id={self.id}, amount={self.amount}, expected_return={self.expected_return}, invested_date={self.invested_date})>'

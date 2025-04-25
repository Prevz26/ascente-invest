import uuid
import sqlalchemy as sa
from base.model import BaseModel
import enum
from sqlalchemy.orm import relationship, backref


class Plan(BaseModel):
    __tablename__ = "plans"
    id = sa.Column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    name = sa.Column(sa.String(30), nullable=False, unique=True)
    duration = sa.Column(sa.String, nullable=False)
    rate_of_return = sa.Column(sa.DECIMAL(10,2), nullable=False)
    status = sa.Column(sa.String(20), nullable=False, default='active')
    minimum = sa.Column(sa.Integer, nullable=False)
    maximum = sa.Column(sa.Integer, nullable=True)

    
    
    @property
    def amount_to_receive(self):
        return f"Capital * {self.rate_of_return}"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'duration': str(self.duration),
            'rate_of_return': self.rate_of_return,
            'status': self.status,
            'minimum': self.minimum,
            'maximum': self.maximum,
            "amount_to_receive": self.amount_to_receive
        }

    def __repr__(self):
        return f"Plan(id={self.id}, plan='{self.plan}', duration={self.duration}, rate_of_return={self.rate_of_return}, status='{self.status}')"
    

class TokenType(enum.Enum):
        btc = 'btc'
        eth = 'eth'
        usdt = 'trc20/usdt'
        trx = 'trx'

class Wallet(BaseModel):
    __tablename__ = "wallets"
    id = sa.Column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    balance = sa.Column(sa.Float, default=0.0, nullable=False) #usd 


    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), unique=True, nullable=False)
    user = relationship("User", backref=backref("wallet", uselist=False)) 


    
    def to_dict(self):
        return {
            'id': self.id,
            'balance': self.balance,
            'user_id': self.user_id
        }

    # transactions = relationship("Transcations", back_populates="wallet")
    # investments = relationship("Investments", back_populates="wallet")


    def __repr__(self):
        return f"Wallet(id={self.id}, token='{self.token.value}', balance={self.balance}, user_id={self.user_id})"


class TransactionStatus(enum.Enum):
    pending = 'pending'
    failed = 'failed'
    success = 'success'

class Transaction(BaseModel):
    __tablename__ = "transactions"
    id = sa.Column(sa.Integer, primary_key=True, unique=True, autoincrement=True)
    transaction_id = sa.Column(sa.String(200),  unique=True)
    transaction_type = sa.Column(sa.String, nullable=False)
    token = sa.Column(sa.String, nullable=False)
    previous_balance = sa.Column(sa.Float, default=0.0)
    present_balance = sa.Column(sa.Float, default=0.0)
    status = sa.Column(
        sa.Enum(TransactionStatus),
        nullable=False,
        default=TransactionStatus.pending
    )
    blockchain_in = sa.Column(sa.String(255), nullable=True)
    blockchain_out = sa.Column(sa.String(255), nullable=True)
    crytp_api_uuid = sa.Column(sa.String(255), nullable=True)

    #foreign key and relationships 
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    wallet_id = sa.Column(sa.Integer, sa.ForeignKey('wallets.id'))
    plan_id = sa.Column(sa.Integer, sa.ForeignKey('plans.id'))
    user = sa.orm.relationship('User', backref='transactions')
    wallet = sa.orm.relationship('Wallet', backref='transactions')
    plan = sa.orm.relationship('Plan', backref='transactions')


    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'wallet_id': self.wallet_id,
            'previous_balance': self.previous_balance,
            'present_balance': self.present_balance,
            'status': self.status.value,
            'blockchain_in': self.blockchain_in,
            'blockchain_out': self.blockchain_out,
            'crytp_api_uuid': self.crytp_api_uuid
        }

    def __repr__(self):
        return f"Transaction(id={self.id}, user_id={self.user_id}, status='{self.status.value}', previous_balance={self.previous_balance}, present_balance={self.present_balance})"


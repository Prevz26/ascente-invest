import uuid
import sqlalchemy as sa
from base.model import BaseModel
import enum

class Plans(BaseModel):
    __tablename__ = "plans"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(30), nullable=False)
    duration = sa.Column(sa.Integer, nullable=False)
    rate = sa.Column(sa.Integer, nullable=False)

    investments = sa.orm.relationship("Investments", back_populates="plan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'duration': self.duration,
            'rate': self.rate
        }

    def __repr__(self):
        return f"Plan(id={self.id}, name='{self.name}', duration={self.duration})"
    

class TokenType(enum.Enum):
        btc = 'btc'
        eth = 'eth'
        usdt = 'trc20/usdt'
        trx = 'trx'

class Wallet(BaseModel):
    __tablename__ = "wallets"
    id = sa.Column(sa.Integer, primary_key=True)
    token = sa.Column(
        sa.Enum(TokenType),
        nullable=False,
        default=TokenType.btc
    )
    balance = sa.Column(sa.Float, default=0.0)

    transaction = sa.orm.relationship("Transcations", back_populates="wallet")

    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    user = sa.orm.relationship('User', back_populates='wallets')

    investments = sa.orm.relationship("Investments", back_populates="wallets")

   
def to_dict(self):
    return {
        'id': self.id,
        'token': self.token.value,
        'balance': self.balance,
        'user_id': self.user_id
    }



def __repr__(self):
    return f"Wallet(id={self.id}, token='{self.token.value}', balance={self.balance}, user_id={self.user_id})"


class TransactionStatus(enum.Enum):
    pending = 'pending'
    failed = 'failed'
    success = 'success'

class Transactions(BaseModel):
    __tablename__ = "transactions"
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    wallet_id = sa.Column(sa.Integer, sa.ForeignKey('wallets.id'))

    user = sa.orm.relationship('User', back_populates='transactions')
    wallet = sa.orm.relationship('Wallet', back_populates='transactions')

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


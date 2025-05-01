from datetime import datetime
from pydantic import BaseModel

class PlanSchema(BaseModel):
    name: str
    rate_of_return: float
    duration: str


class InvestmentProfit(BaseModel):
    investment_id: int
    user_id: int
    plan_id: int
    amount_invested: float
    invested_date: datetime
    maturity_date: datetime
    is_matured: bool
    profit: float
    total_payout: float
    status: str
    wallet_id: int
    
class InvestmentSchema(BaseModel):
    id: int
    amount: float
    status: str
    invested_date: datetime | None = None
    last_viewed: datetime | None = None
    profit_added: datetime | None = None
    user_id: int
    wallet_id: int | None = None
    plan_id: int
    is_active: bool
    profit: float
    total_payout: float
    maturity_date: str | None = None
    maturity_date_obj: datetime | None = None
    is_matured: bool
    created_at: datetime | None = None
    plan: PlanSchema | None = None
    updated_at: datetime | None = None

class AllInvestmentSchema(BaseModel):
    data: list[InvestmentSchema]
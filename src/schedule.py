from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
from v1.plans.service import wallet_service

scheduler = BackgroundScheduler()
# Schedule the fund_wallet_with_daily_profit function to run every 24 hours
scheduler.add_job(wallet_service.fund_wallet_with_daily_profit, 'interval', hours=1)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())
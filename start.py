from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.reminder import send_reminders

def create_scheduler(app):
    scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")
    scheduler.add_job(
        send_reminders,
        trigger='cron',
        day='15-31',
        hour=8,         #jam 08:00 WIB
        minute=0,   
        args=[app],
        id='daily_invoice_reminder'
    )
    return scheduler
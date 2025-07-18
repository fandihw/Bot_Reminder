from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.reminder import send_reminders

def create_scheduler(app):
    scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")
    scheduler.add_job(
        send_reminders,
        trigger='cron',
        day='15-31',
        hour=10,         #jam 08:00 WIB
        minute=5,
        second=0,  #<----- buat testing 
        args=[app],
        id='daily_invoice_reminder'
    )
    return scheduler
# start.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.reminder import send_reminders

def create_scheduler(app):
    scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")
    scheduler.add_job(
        send_reminders,
        trigger='cron',
        day='15-31',
        hour=11,
        minute=30,
        args=[app],
        id='daily_invoice_reminder'
    )
    return scheduler

'''
def schedule_reminder(app):
    app.job_queue.run_once(
        send_reminders,
        when=5,
        name="test_reminder"
    )
    '''
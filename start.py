from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.reminder import send_reminders
from handlers.report import send_daily_keterangan_report

async def send_all_reports(app):
    await send_reminders(app)
    await send_daily_keterangan_report(app.bot)

def create_scheduler(app):
    scheduler = AsyncIOScheduler(timezone="Asia/Jakarta")
    scheduler.add_job(
        send_all_reports,
        trigger='cron',
        day='15-31',
        hour=8,    # 08:00 WIB 
        minute=0,
        second=0,  # testing
        args=[app],
        id='daily_invoice_reminder'
    )
    return scheduler

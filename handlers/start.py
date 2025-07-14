from apscheduler.schedulers.background import BackgroundScheduler
from handlers.reminder import send_reminders

def schedule_reminder():
    scheduler = BackgroundScheduler(timezone="Asia/Jakarta")
    scheduler.add_job(send_reminders, 'cron', day='15-31', hour=9, minute=0)
    scheduler.start()
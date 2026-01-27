from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import time

class ReminderScheduler:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ReminderScheduler, cls).__new__(cls)
            cls._instance.scheduler = BackgroundScheduler()
            cls._instance.scheduler.start()
        return cls._instance

    def schedule_prescription(self, prescription_id, medicine_name, times):
        """
        Schedules reminders for a prescription.
        times: List of "HH:MM"
        """
        from src.services.database import Database
        db = Database()
        
        # Simple Logic: Schedule for next 7 days for demo
        # In production, this would be a daily recurring job
        
        for time_str in times:
            hour, minute = map(int, time_str.split(':'))
            
            # Add job to scheduler (cron style for daily)
            job_id = f"pres_{prescription_id}_{hour}_{minute}"
            
            # Avoid duplicate jobs
            if self.scheduler.get_job(job_id):
                continue

            self.scheduler.add_job(
                self._send_reminder,
                CronTrigger(hour=hour, minute=minute),
                args=[prescription_id, medicine_name],
                id=job_id,
                replace_existing=True
            )
            
            # Also add to DB reminders table immediately for the next occurrence
            # (Simplified: just logging 15 occurrences into the future to show in UI)
            # This is a bit hacky for a demo, a real app generates them on fly.
            self._generate_future_db_reminders(db, prescription_id, hour, minute)

    def _generate_future_db_reminders(self, db, prescription_id, hour, minute):
        """Generates mock future reminders in DB so they show up in UI"""
        import datetime
        now = datetime.datetime.now()
        
        for i in range(7): # Next 7 days
            reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + datetime.timedelta(days=i)
            if reminder_time < now: 
                reminder_time += datetime.timedelta(days=1)
                
            db.add_reminder(prescription_id, reminder_time)

    def _send_reminder(self, prescription_id, medicine_name):
        print(f"⏰ REMINDER: Time to take {medicine_name}!")
        
        # 1. Update DB status
        from src.services.database import Database
        db = Database()
        # Find pending reminder close to now and mark sent
        # (Implementation omitted for brevity)
        
        # 2. Send Email
        from src.services.email_service import EmailService
        email_svc = EmailService()
        # Fetch user email from DB (mocking here)
        user_email = "ubaidzafar05@gmail.com" # Hardcoded for demo/verification
        
        email_svc.send_email(
            user_email,
            f"Medicine Reminder: {medicine_name}",
            f"Hi! It's time to take your {medicine_name}. Stay healthy!"
        )

import smtplib
from email.mime.text import MIMEText
from src.config import SMTP_USERNAME, SMTP_PASSWORD

class EmailService:
    def send_email(self, to_email, subject, body):
        try:
            msg = MIMEText(body, 'html')
            msg['Subject'] = subject
            msg['From'] = SMTP_USERNAME
            msg['To'] = to_email

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                smtp_server.login(SMTP_USERNAME, SMTP_PASSWORD)
                smtp_server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
            print(f"📧 Email sent to {to_email}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")

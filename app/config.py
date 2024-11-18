import os

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.mailer91.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "emailer@aroundme.tech")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", None)

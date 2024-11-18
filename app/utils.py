import re, os
import smtplib
from openai import OpenAI
from datetime import datetime
from email.mime.text import MIMEText
from app.config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
from app import app

api_key = os.getenv("OPENAI_API_KEY", "default_api_key")
client = OpenAI(api_key=api_key)


def personalize_email(template, row_data):
    placeholders = re.findall(r"\{\{\s*(\w+)\s*\}\}", template)

    missing = [p for p in placeholders if p not in row_data]
    if missing:
        raise ValueError(f"Missing data for placeholders: {', '.join(missing)}")

    for key, value in row_data.items():
        template = template.replace(f"{{{{ {key} }}}}", str(value))

    return template


def update_email_stats(email, status, scheduled_time=None):
    try:
        if not email or not status:
            raise ValueError("Email and status are required")

        now = datetime.now().isoformat()
        email_data = {
            "status": str(status),
            "timestamp": str(now),
            "scheduled_time": str(scheduled_time) if scheduled_time else "",
        }

        app.redis.hset(f"email:{email}", mapping=email_data)

        app.redis.srem("status:scheduled", email)
        app.redis.srem("status:sent", email)
        app.redis.srem("status:failed", email)
        app.redis.sadd(f"status:{status}", email)

        return True
    except Exception as e:
        print(f"Error updating email stats: {str(e)}")
        return False


def send_email(recipient, subject, body):
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = SMTP_USERNAME
    msg["To"] = recipient

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True, "Email sent successfully."
    except Exception as e:
        return False, str(e)


def generate_email_content(prompt):
    if not prompt or not isinstance(prompt, str):
        print("Error: Invalid prompt provided")
        return None

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an email writing assistant. Generate only the body content of professional emails. Keep the tone business-appropriate and concise.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=250,
            temperature=0.4,
            presence_penalty=0.1,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Email body generation failed: {str(e)}")
        return None

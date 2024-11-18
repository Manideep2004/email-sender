from celery import Celery
from app import app as flask_app
from app.utils import (
    send_email,
    generate_email_content,
    personalize_email,
    update_email_stats,
)

celery = Celery(
    "tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery.task(rate_limit="50/h", bind=True)  # rate-limiting
def send_scheduled_email(self, recipient, subject, prompt, row_data):
    try:
        personalized_prompt = personalize_email(prompt, row_data)
        email_body = generate_email_content(personalized_prompt)
        if email_body:
            success, message = send_email(recipient, subject, email_body)
            status = "sent" if success else "failed"
            update_email_stats(recipient, status)
            return success, message
        update_email_stats(recipient, "failed")
        return False, "Failed to generate email content"
    except Exception as e:
        update_email_stats(recipient, "failed")
        return False, str(e)

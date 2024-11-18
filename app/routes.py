import os
from flask import request, render_template, flash, jsonify
from app.utils import (
    send_email,
    personalize_email,
    generate_email_content,
    update_email_stats,
)
from app import app
import pandas as pd
from datetime import datetime
from app.scheduler import send_scheduled_email


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/email-stats")
def email_stats():
    stats = {
        "sent": list(app.redis.smembers("status:sent")),
        "failed": list(app.redis.smembers("status:failed")),
        "scheduled": list(app.redis.smembers("status:scheduled")),
    }

    details = {}
    for status in stats:
        for email in stats[status]:
            details[email] = app.redis.hgetall(f"email:{email}")

    history = []
    timeline = app.redis.zrange("email_timeline", 0, -1, withscores=True)
    for event_id, timestamp in timeline:
        event_data = app.redis.hgetall(f"email_history:{event_id}")
        if event_data:
            email = event_id.split(":")[0]
            history.append({"email": email, **event_data})

    return jsonify(
        {
            "counts": {k: len(v) for k, v in stats.items()},
            "details": details,
            "history": history,
        }
    )


@app.route("/upload_csv", methods=["GET", "POST"])
def upload_csv():
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename.endswith(".csv"):
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)

            data = pd.read_csv(file_path)
            columns = data.columns.tolist()

            return render_template(
                "upload_success.html", columns=columns, file=file.filename
            )

        flash("Invalid file type. Please upload a CSV file.", "danger")
    return render_template("upload_csv.html")


@app.route("/send_emails", methods=["POST"])
def send_emails():
    file = request.form.get("file")
    subject = request.form.get("subject")
    prompt = request.form.get("prompt")
    schedule_time = request.form.get("schedule_time")

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file)
    data = pd.read_csv(file_path)
    results = []

    schedule_dt = None
    if schedule_time:
        schedule_dt = datetime.fromisoformat(schedule_time)
        if schedule_dt.tzinfo is None:
            schedule_dt = schedule_dt.astimezone()

    for _, row in data.iterrows():
        row_data = row.to_dict()
        if schedule_dt:
            task = send_scheduled_email.apply_async(
                args=[row["Email"], subject, prompt, row_data], eta=schedule_dt
            )
            update_email_stats(row["Email"], "scheduled", schedule_time)
            results.append(
                {
                    "email": row["Email"],
                    "status": "Scheduled",
                    "message": f"Email scheduled for {schedule_time}",
                    "task_id": task.id,
                }
            )
        else:
            personalized_prompt = personalize_email(prompt, row_data)
            email_body = generate_email_content(personalized_prompt)
            if email_body:
                success, message = send_email(row["Email"], subject, email_body)
                status = "sent" if success else "failed"
                update_email_stats(row["Email"], status)
                results.append(
                    {
                        "email": row["Email"],
                        "status": "Success" if success else "Failed",
                        "message": message,
                    }
                )
            else:
                results.append(
                    {
                        "email": row["Email"],
                        "status": "Failed",
                        "message": "AI content generation failed.",
                    }
                )

    return render_template("email_status.html", results=results)

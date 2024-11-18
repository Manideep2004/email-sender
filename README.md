Overview
This web application allows users to send customized emails using a combination of Celery for task management, Redis for data storage and scheduling, and the OpenAI API for generating personalized email content based on user-provided data (CSV file). The application also provides a user-friendly dashboard to track the status of emails (sent, scheduled, failed) and includes functionality to schedule emails for future delivery.

Features
Custom Email Generation: Leverages OpenAI's API to generate personalized email content based on the data from a provided CSV file.
Email Scheduling: Allows users to schedule emails for specific dates and times.
Task Management: Uses Celery to manage email-sending tasks asynchronously.
Data Storage: Employs Redis as a fast, reliable, and scalable data store.
Dashboard:
View the status of emails: sent, scheduled, failed.
Monitor the progress of tasks in real-time.

Usage
Upload CSV File:

Upload a CSV file containing the user data (e.g., name, email, preferences).
Generate Custom Prompts:

The OpenAI API will use the uploaded data to create personalized email content.
Schedule Emails:

Select a specific date and time for sending emails, or send them immediately.
Monitor Dashboard:

View the current status of emails:
Sent: Emails successfully delivered.
Scheduled: Emails scheduled for future delivery.
Failed: Emails that encountered an error.
Retry or Reschedule:

Retry failed emails or adjust the schedule for pending emails directly from the dashboard.

Technologies Used
Backend:

Flask
Celery for asynchronous task management
Redis for data storage and scheduling
OpenAI API for content generation

Frontend:
HTML/JavaScript for user interface

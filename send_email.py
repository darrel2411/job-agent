import os
import json
import html
import smtplib
from datetime import date
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

GMAIL = os.getenv("GMAIL_ADDRESS")
PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
TO = os.getenv("EMAIL_TO") or GMAIL

MIN_SCORE = 5  # only show jobs with this score or higher


def badge_color(score):
    if score >= 8:
        return "#16a34a"  # green
    if score >= 6:
        return "#2563eb"  # blue
    return "#6b7280"      # gray


def job_card(job):
    e = html.escape
    location = e(job.get("city") or "Canada")
    if job.get("remote"):
        location += " · Remote"

    flags = "".join(f"<li>{e(f)}</li>" for f in job.get("red_flags", []))
    flags_html = (
        f'<ul style="margin:8px 0 0;padding-left:18px;color:#b45309;font-size:13px;">{flags}</ul>'
        if flags else ""
    )

    return f"""
    <div style="border:1px solid #e5e7eb;border-radius:10px;padding:16px;margin-bottom:12px;">
      <div style="display:flex;align-items:center;gap:10px;">
            <span style="background:{badge_color(job['score'])};color:#fff;font-weight:bold;
                    border-radius:6px;padding:4px 10px;font-size:14px;margin-right:8px;">{job['score']}</span>
        <a href="{e(job.get('link') or '#', quote=True)}"
           style="font-size:16px;font-weight:bold;color:#111827;text-decoration:none;">{e(job['title'] or '')}</a>
      </div>
      <div style="color:#4b5563;font-size:14px;margin-top:6px;">{e(job['company'] or '')} · {location}</div>
      <div style="font-size:14px;margin-top:8px;">{e(job.get('reason', ''))}</div>
      {flags_html}
    </div>
    """


def build_html(good_jobs, total):
    if good_jobs:
        body = "".join(job_card(j) for j in good_jobs)
    else:
        body = '<p style="color:#6b7280;">No good matches today.</p>'

    return f"""
    <div style="font-family:Arial,sans-serif;max-width:640px;margin:auto;padding:16px;">
      <h2 style="margin:0 0 4px;">Job matches for {date.today():%b %d}</h2>
      <p style="color:#6b7280;margin:0 0 16px;font-size:14px;">
        {len(good_jobs)} of {total} new jobs scored {MIN_SCORE}+
      </p>
      {body}
    </div>
    """


def send_digest(scored_jobs):
    good = [j for j in scored_jobs if j.get("score", 0) >= MIN_SCORE]

    msg = MIMEText(build_html(good, len(scored_jobs)), "html")
    msg["Subject"] = f"{len(good)} job matches · {date.today():%b %d}"
    msg["From"] = GMAIL
    msg["To"] = TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL, PASSWORD)
        server.send_message(msg)

    print(f"Sent email with {len(good)} jobs to {TO}")


if __name__ == "__main__":
    with open("scored_jobs.json") as f:
        jobs = json.load(f)
    send_digest(jobs)
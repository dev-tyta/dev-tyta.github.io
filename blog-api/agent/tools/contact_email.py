"""
Contact email tool — sends user messages to Testimony's inbox.
Requires SMTP credentials. Formats a clean email with chat context.
"""

import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from langchain_core.tools import tool

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "hardeykoryar7@gmail.com")


@tool
def send_contact_message(
    visitor_name: str,
    visitor_email: str,
    message: str,
    topic: str = "Portfolio inquiry",
) -> str:
    """
    Send a contact message from a portfolio visitor to Testimony's inbox.
    Use ONLY after you have collected all three: visitor's name, email, and message.
    Do NOT call this with placeholder or empty values.

    Args:
        visitor_name: The visitor's full name.
        visitor_email: The visitor's email address (must be a valid email).
        message: The visitor's message to Testimony.
        topic: Brief topic / subject (e.g. "Collaboration", "Hiring", "Research").
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        return (
            "[EMAIL] SMTP not configured on this server. "
            "Please email Testimony directly at testimonyadekoya.02@gmail.com"
        )

    if not visitor_email or "@" not in visitor_email:
        return "Invalid email address provided. Please ask the visitor for a valid email."

    if not visitor_name.strip() or not message.strip():
        return "Missing visitor name or message. Please collect both before sending."

    subject = f"[Portfolio Contact] {topic} — from {visitor_name}"

    html_body = f"""
    <html><body style="font-family:sans-serif;color:#111;max-width:600px">
      <h2 style="color:#3b82f6">New message from your portfolio</h2>
      <table style="border-collapse:collapse;width:100%">
        <tr><td style="padding:8px;font-weight:bold;color:#555">From</td>
            <td style="padding:8px">{visitor_name}</td></tr>
        <tr><td style="padding:8px;font-weight:bold;color:#555">Email</td>
            <td style="padding:8px"><a href="mailto:{visitor_email}">{visitor_email}</a></td></tr>
        <tr><td style="padding:8px;font-weight:bold;color:#555">Topic</td>
            <td style="padding:8px">{topic}</td></tr>
      </table>
      <hr style="border:1px solid #eee;margin:16px 0">
      <h3 style="color:#555">Message</h3>
      <p style="line-height:1.7;background:#f9f9f9;padding:16px;border-radius:8px">{message}</p>
      <p style="color:#888;font-size:12px">Sent via Testimony's portfolio digital double at dev-tyta.github.io</p>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = CONTACT_EMAIL
    msg["Reply-To"] = visitor_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, CONTACT_EMAIL, msg.as_string())
        return (
            f"Message sent successfully to Testimony. "
            f"He'll reply to {visitor_email} — usually within a day or two."
        )
    except smtplib.SMTPAuthenticationError:
        return "[EMAIL] Authentication failed. Check SMTP credentials."
    except smtplib.SMTPException as e:
        return f"[EMAIL] Failed to send: {str(e)[:120]}"
    except Exception as e:
        return f"[EMAIL] Unexpected error: {str(e)[:120]}"

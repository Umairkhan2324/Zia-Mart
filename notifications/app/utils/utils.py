import emails
from app import settings
import requests
from pathlib import Path
from jinja2 import Template

def get_user_by_id(customer_id: int):
    """Fetch user details by customer ID from the authentication server."""
    url = f"{settings.AUTH_SERVER_URL}/get-user-by-id?user_id={customer_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def send_email(*, email_to: str, subject: str, email_content_for_send: str) -> None:
    """Send an email using the configured SMTP settings."""
    assert settings.emails_enabled, "Email configuration is not enabled."

    message = emails.Message(
        subject=subject,
        html=email_content_for_send,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )

    smtp_options = {
        "host": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
        "tls": settings.SMTP_TLS,
        "ssl": settings.SMTP_SSL,
        "user": settings.SMTP_USER if settings.SMTP_USER else None,
        "password": settings.SMTP_PASSWORD if settings.SMTP_PASSWORD else None
    }

    smtp_options = {key: value for key, value in smtp_options.items() if value is not None}

    response = message.send(to=email_to, smtp=smtp_options)

    print(f"Email response: {response}")

def email_content(context: dict, template_name: str) -> str:
    """Generate email content by rendering a Jinja2 HTML template with context."""
    template_path = Path(__file__).parent.parent / "templates" / template_name
    template_str = template_path.read_text()
    return Template(template_str).render(context)

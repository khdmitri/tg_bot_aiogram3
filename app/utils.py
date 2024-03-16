from pathlib import Path
from typing import Dict, Any

import emails
from emails.template import JinjaTemplate

from app.core.config import settings
from utils.logger import get_logger

logger = get_logger()


def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logger.info(f"send email result: {response}")


def send_greeting_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME
    project_link = settings.PROJECT_LINK
    link_tg_app = settings.LINK_TG_APP
    link_tg_channel = settings.LINK_TG_CHANNEL
    link_tg_group = settings.LINK_TG_GROUP
    link_tg_bot = settings.LINK_TG_BOT
    subject = f"{project_name} - Мы получили ваш e-mail"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "greetings.html") as f:
        template_str = f.read()
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": project_name,
            "project_link": project_link,
            "link_tg_app": link_tg_app,
            "link_tg_channel": link_tg_channel,
            "link_tg_group": link_tg_group,
            "link_tg_bot": link_tg_bot,
        },
    )

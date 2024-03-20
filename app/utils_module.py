import os.path
from typing import Dict, Any

import emails
from emails.template import JinjaTemplate

from app.core.config import settings
from app.definitions import ROOT_DIR
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
    logo = "https://postmasterhub.store/api/v2/document/get_logo/"
    link_site = settings.LINK_SITE
    subject = f"{project_name} - Мы получили ваш e-mail"
    with open(os.path.join(ROOT_DIR, settings.EMAIL_TEMPLATES_DIR, "greetings.html")) as f:
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
            "logo": logo,
            "link_site": link_site,
        },
    )


def send_promotion_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME
    project_link = settings.PROJECT_LINK
    link_tg_app = settings.LINK_TG_APP
    link_tg_channel = settings.LINK_TG_CHANNEL
    link_tg_group = settings.LINK_TG_GROUP
    link_tg_bot = settings.LINK_TG_BOT
    logo = "https://postmasterhub.store/api/v2/document/get_logo/"
    promotion_link = settings.PROMOTION_LINK
    link_site = settings.LINK_SITE
    subject = f"{project_name} - Запрос на закрытый урок"
    with open(os.path.join(ROOT_DIR, settings.EMAIL_TEMPLATES_DIR, "promotion.html")) as f:
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
            "logo": logo,
            "link_site": link_site,
            "promotion_link": promotion_link,
        },
    )


def send_paid_email(email_to: str, telegram_link: str, disk_link) -> None:
    project_name = settings.PROJECT_NAME
    project_link = settings.PROJECT_LINK
    link_tg_app = settings.LINK_TG_APP
    link_tg_channel = settings.LINK_TG_CHANNEL
    link_tg_group = settings.LINK_TG_GROUP
    link_tg_bot = settings.LINK_TG_BOT
    logo = "https://postmasterhub.store/api/v2/document/get_logo/"
    link_site = settings.LINK_SITE
    subject = f"{project_name} - Запрос на закрытый урок"
    with open(os.path.join(ROOT_DIR, settings.EMAIL_TEMPLATES_DIR, "paid.html")) as f:
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
            "logo": logo,
            "link_site": link_site,
            "telegram_link": telegram_link,
            "disk_link": disk_link,
        },
    )

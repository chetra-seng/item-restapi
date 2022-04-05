import os
from typing import List
from requests import Response, post

FAILED_LOAD_API_KEY = "Failed to load MailGun API key."
FAILED_LOAD_DOMAIN = "Failed to load MailGun domain"
ERROR_SENDING_EMAIL = "Failed to send email to recipient."


class MailGunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class MailGun:
    MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
    MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
    FROM_TITLE = "Store Rest API"
    FROM_EMAIL = "chetra.ballistic@gmail.com"

    @classmethod
    def send_email(cls, email: List[str], subject: str, text: str) -> Response:
        if cls.MAILGUN_API_KEY is None:
            raise MailGunException(FAILED_LOAD_API_KEY)
        if cls.MAILGUN_DOMAIN is None:
            raise MailGunException(FAILED_LOAD_DOMAIN)
        response = post(
            cls.MAILGUN_DOMAIN,
            auth=("api", cls.MAILGUN_API_KEY),
            data = {
                "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text
            }
        )

        if response.status_code != 200:
            raise MailGunException(ERROR_SENDING_EMAIL)
        
        return response
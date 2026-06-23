import base64

from email.mime.text import MIMEText
from googleapiclient.errors import HttpError


def email_sender(gmail_service, sender: str, receiver: str, subject: str, body: str):
    """
    Send an email with a confirmed schedule through Gmail API

    Args:
        gmail_service : Gmail service object
        sender (str): sender email
        receiver (str): receiver email
        subject (str): email subject
        body (str): email body
    """

    message = MIMEText(body)

    message["to"] = receiver
    message["from"] = sender
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    try:
        result = (
            gmail_service.users()
            .messages()
            .send(
                userId="me",
                body={
                    "raw": raw_message
                }
            )
            .execute()
        )
        return result
    except HttpError as e:
        raise RuntimeError(f"Error sending an email through Gmail: {e}\n")
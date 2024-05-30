import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

from dotenv import load_dotenv #pip install python-dotenv

PORT = 587
EMAIL_SERVER = "stmp-mail.outlook.com"

#load environment variables
current_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
envars = current_dir / ".env"
load_dotenv(envars)

#Read environmental variables
sender_email = os.gatenv("EMAIL")
password_email = os.gatenv("PASSWORD")

def send_email(subject, recevier_mail, name, address):
    # Create a base text message
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr(("Wildfire Alet!", f"{sender_email}"))
    msg["To"] = recevier_mail
    

    msg.set_content(
    f"""\
    Hi{name}
    There is a wildfire predected near this {address}
    This is a automated email for warning
    Please take safety precuations
    """
    )

    msg.add_alternative(
        f"""\
        <html>
        <body>
        <p> Hi{name} <p>
        <p> There is a wildfire predected near this <strong> {address} <strong>  <p>
        <p> This is a automated email for warning <p>
        <p> Please take safety precuations <p>
        <body>
        <html>
        """,
        subtype = "html"
    )

    with smtplib.SMTP(EMAIL_SERVER,PORT) as server:
        server.starttls()
        server.login(sender_email,password_email)
        server.sendmail(sender_email,recevier_mail,msg.as_string())



if __name__ == "__main__":
    send_email(
        subject="Wildfire Alet in your area!",
        name= "john",
        recevier_mail= "testingmail@gmail.com",
        address= """53°44'49.8"N 114°21'19.5"W"""
    )
                              
import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path
from dotenv import load_dotenv
from check_weather import check_alberta_condition


PORT = 587
EMAIL_SERVER = "stmp-mail.outlook.com"

# load environment variables
current_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
envars = current_dir / ".env"
load_dotenv(envars)

# Read environmental variables
sender_email = os.getenv("EMAIL")
password_email = os.getenv("PASSWORD")

def list_email_template(latitude, longitude):
    return f"Latitude:{latitude}, Longitude: {longitude}"


def send_email(subject, recevier_mail, name, address):
    # Create a base text message

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr(("Wildfire Alet!", f"{sender_email}"))
    msg["To"] = recevier_mail

    danger_zone = check_alberta_condition()


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
        <p> This email is to inform you of a possible wildfire in the area.  We have identified potential fire activity at the following locations: <p>
        <ul>
          <li>{list_email_template(latitude=danger_zone[0][0], longitude=danger_zone[0][1])}</li>
          <li>{list_email_template(latitude=danger_zone[1][0], longitude=danger_zone[1][1])}</li>
          <li>{list_email_template(latitude=danger_zone[2][0], longitude=danger_zone[2][1])}</li>
          <li>{list_email_template(latitude=danger_zone[3][0], longitude=danger_zone[3][1])}</li>
          <li>{list_email_template(latitude=danger_zone[4][0], longitude=danger_zone[4][1])}</li>
        </ul>
        <p>
            <strong>Please Note</strong>: These are just potential locations, and the actual fire may be in different area
        </p>
        <body>
        <html>
        """,
        subtype="html"
    )

    with smtplib.SMTP(EMAIL_SERVER, PORT) as server:
        server.starttls()
        server.login(sender_email, password_email)
        server.sendmail(sender_email, recevier_mail, msg.as_string())


if __name__ == "__main__":
    send_email(
        subject="Wildfire Alet in your area!",
        name="john",
        recevier_mail="testingmail@gmail.com",
        address="""53°44'49.8"N 114°21'19.5"W"""
    )

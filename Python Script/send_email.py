import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path
import joblib
from dotenv import load_dotenv
import numpy as np
import pandas as pd

PORT = 587
EMAIL_SERVER = "stmp-mail.outlook.com"

# load environment variables
current_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
envars = current_dir / ".env"
load_dotenv(envars)

# Read environmental variables
sender_email = os.gatenv("EMAIL")
password_email = os.gatenv("PASSWORD")

model = joblib.load('model/padam.joblib')
scaler = joblib.load('model/scaler.joblib')


def predict(scaler, model):
    # Assuming data is sent as a JSON payload
    data = {
        "fire_location_latitude": 53.81625046092191,
        "fire_location_longitude": -117.21135002795386,
        "temperature": 11,
        "relative_humidity": 30,
        "wind_speed": 5,
        "month": 4,
        'weather_conditions_over_fire_CB Dry': False,
        'weather_conditions_over_fire_CB Wet': False,
        'weather_conditions_over_fire_Clear': True,
        'weather_conditions_over_fire_Cloudy': False,
        'weather_conditions_over_fire_Rainshowers': False
    }

    features = np.array([[
        data['fire_location_latitude'],
        data['fire_location_longitude'],
        data['temperature'],
        data['relative_humidity'],
        data['wind_speed'],
        data['month'],
        data['weather_conditions_over_fire_CB Dry'],
        data['weather_conditions_over_fire_CB Wet'],
        data['weather_conditions_over_fire_Clear'],
        data['weather_conditions_over_fire_Cloudy'],
        data['weather_conditions_over_fire_Rainshowers']
    ]])

    # Ensure features have the same structure as the training data
    feature_names = [
        'fire_location_latitude', 'fire_location_longitude',
        'temperature', 'relative_humidity', 'wind_speed', 'month',
        'weather_conditions_over_fire_CB Dry', 'weather_conditions_over_fire_CB Wet',
        'weather_conditions_over_fire_Clear', 'weather_conditions_over_fire_Cloudy',
        'weather_conditions_over_fire_Rainshowers'
    ]
    features_df = pd.DataFrame(features, columns=feature_names)

    # Standardize the features
    features_scaled = scaler.transform(features_df)
    print(features_scaled)

    # Make prediction
    prediction = model.predict(features_scaled)
    prediction_value = prediction[0]

    return prediction_value


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

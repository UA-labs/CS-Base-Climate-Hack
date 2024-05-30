import joblib
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import requests
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import os
import datetime


def predict(environment_condition: dict):
    """
    :param scaler: model/scaler.joblib
    :param model: model/padam.joblib
    :param environment_condition:
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
    :return:
    """
    model = joblib.load('model/padam.joblib')
    scaler = joblib.load('model/scaler.joblib')
    features = np.array([[
        environment_condition['fire_location_latitude'],
        environment_condition['fire_location_longitude'],
        environment_condition['temperature'],
        environment_condition['relative_humidity'],
        environment_condition['wind_speed'],
        environment_condition['month'],
        environment_condition['weather_conditions_over_fire_CB Dry'],
        environment_condition['weather_conditions_over_fire_CB Wet'],
        environment_condition['weather_conditions_over_fire_Clear'],
        environment_condition['weather_conditions_over_fire_Cloudy'],
        environment_condition['weather_conditions_over_fire_Rainshowers']
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


def call_api_data(latitude: float, longtitude: float) -> dict:
    """
    :param: latitude, longtitude
    :return: dictionary of weather data
    """
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    base_url = f"https://api.openweathermap.org/data/2.5/weather?lat={round(latitude, 2)}&lon={round(longtitude, 2)}&appid={API_KEY}"

    response = requests.get(base_url)
    data = response.json()

    return data

def check_weather_condition(data: dict):
    if data["weather"] == "Clear":
        data['weather_conditions_over_fire_Clear'] = True
    elif data["weather"] == "Clouds":
        data['weather_conditions_over_fire_Cloudy'] = True
    elif data["weather"] == "Rain":
        data['weather_conditions_over_fire_Rainshowers'] = True

def convert_timestamp(timestamp):
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    # Extract the month
    month = dt_object.month
    return month

def load_weather_data(data: dict) -> dict:
    """
    :param data: data that we get from the API call
    :return: cleaned dictionary for latitude, longitude, temperature, relative humidity, wind speed, month, weather condition
    """
    # If the response contains the 'main' field, it was successful
    data = {
        "coord": {
            "lon": 10.99,
            "lat": 44.34
        },
        "weather": [
            {
                "id": 501,
                "main": "Rain",
                "description": "moderate rain",
                "icon": "10d"
            }
        ],
        "base": "stations",
        "main": {
            "temp": 298.48,
            "feels_like": 298.74,
            "temp_min": 297.56,
            "temp_max": 300.05,
            "pressure": 1015,
            "humidity": 64,
            "sea_level": 1015,
            "grnd_level": 933
        },
        "visibility": 10000,
        "wind": {
            "speed": 0.62,
            "deg": 349,
            "gust": 1.18
        },
        "rain": {
            "1h": 3.16
        },
        "clouds": {
            "all": 100
        },
        "dt": 1661870592,
        "sys": {
            "type": 2,
            "id": 2075663,
            "country": "IT",
            "sunrise": 1661834187,
            "sunset": 1661882248
        },
        "timezone": 7200,
        "id": 3163858,
        "name": "Zocca",
        "cod": 200
    }
    if data["cod"] != "404":
        main = data["main"]
        temperature = main["temp"]
        wind_speed = data['wind']['speed']
        humidity = main["humidity"]
        report = data["weather"][0]['main']
        month = convert_timestamp(data['dt'])
        return_dict = {
            'temprature': temperature,
            'humidity': humidity,
            'weather': report,
            'wind speed': wind_speed,
            'month': month,
            'weather_conditions_over_fire_CB Dry': False,
            'weather_conditions_over_fire_CB Wet': False,
            'weather_conditions_over_fire_Clear': False,
            'weather_conditions_over_fire_Cloudy': False,
            'weather_conditions_over_fire_Rainshowers': False
        }
        check_weather_condition(return_dict)
        return_dict.pop('weather')
        return return_dict
    else:
        raise ValueError


data ={}
print(load_weather_data(data))

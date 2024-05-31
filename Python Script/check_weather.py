import joblib
import pandas
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import requests
import os
import datetime


def load_dataset():
    """
    :return: pandas dataframe
    """
    dataset = pd.read_csv('fp-historical-wildfire-data-2006-2023-filtered - Data.csv')
    return dataset


def predict(environment_condition: dict):
    """
    :param environment_condition:
    :return: prediction value
    """
    model = joblib.load('padam.joblib')
    scaler = joblib.load('scaler.joblib')
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
    API_KEY = os.getenv("OPEN_WEATHER_API_KEY")
    print(API_KEY)  # This should print your API key if it's loaded correctly
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


def load_weather_data(data: dict, lat: float, lon: float) -> dict:
    """
    :param data: data that we get from the API call
    :param lat: latitude of the location
    :param lon: longitude of the location
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
            'fire_location_latitude': lat,
            'fire_location_longitude': lon,
            'temperature': temperature,
            'relative_humidity': humidity,
            'weather': report,
            'wind_speed': wind_speed,
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


def get_coordinate(dataset: pandas.core.frame.DataFrame):
    dataset["fire_location_latitude"] = dataset["fire_location_latitude"].round(2)
    dataset["fire_location_longitude"] = dataset["fire_location_longitude"].round(2)

    # Remove duplicate rows
    dataset.drop_duplicates(subset=["fire_location_latitude", "fire_location_longitude"], keep='first', inplace=True)

    latitude = dataset["fire_location_latitude"]
    longitude = dataset["fire_location_longitude"]

    dataset = {
        'latitude': latitude,
        'longitude': longitude
    }
    return dataset

def check_alberta_condition():
    # Load the dataset
    dataset = get_coordinate(load_dataset())
    danger_zone = {}
    danger_zone_count = 0

    # Loop through all the latitude and longitude values
    for lat, lon in zip(dataset['latitude'], dataset['longitude']):
        # Call the API to get the weather data
        weather_data = call_api_data(lat, lon)

        # Process the weather data
        processed_data = load_weather_data(weather_data, lat, lon)

        # You can now use the processed_data for further processing or analysis
        prediction = predict(processed_data)
        if prediction >= 0.6:
            danger_zone[danger_zone_count] = [lat, lon]
            danger_zone_count += 1
            if danger_zone_count == 5:
                break
    return danger_zone


def main():
    dataset = load_dataset()
    get_coordinate(dataset=dataset)
    print("return", check_alberta_condition())


if __name__ == '__main__':
    main()

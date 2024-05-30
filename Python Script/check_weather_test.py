import unittest
from unittest.mock import patch, Mock
import pandas as pd
import numpy as np
from check_weather import predict, check_location

class TestWeatherPrediction(unittest.TestCase):

    @patch('check_weather.joblib.load')
    def test_predict_with_valid_data(self, mock_load):
        mock_model = Mock()
        mock_model.predict.return_value = [0.6]
        mock_scaler = Mock()
        mock_scaler.transform.return_value = np.array([[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0, 0, 1, 0, 0]])
        mock_load.side_effect = [mock_model, mock_scaler]

        environment_condition = {
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

        result = predict('model/scaler.joblib', 'model/padam.joblib', environment_condition)
        self.assertEqual(result, 0.6)

    @patch('check_weather.os.getenv')
    @patch('check_weather.requests.get')
    def test_check_location_with_valid_data(self, mock_get, mock_getenv):
        mock_getenv.return_value = 'dummy_api_key'
        mock_response = Mock()
        mock_response.json.return_value = {
            "cod": "200",
            "main": {
                "temp": 11,
                "pressure": 1013,
                "humidity": 30
            },
            "weather": [
                {
                    "main": "Clear",
                    "description": "clear sky"
                }
            ]
        }
        mock_get.return_value = mock_response

        result = check_location('53.81625046092191', '-117.21135002795386')
        expected_result = {
            'temprature': 11,
            'humidity': 30,
            'weather': [
                {
                    "main": "Clear",
                    "description": "clear sky"
                }
            ]
        }
        self.assertEqual(result, expected_result)

    @patch('check_weather.os.getenv')
    @patch('check_weather.requests.get')
    def test_check_location_with_invalid_data(self, mock_get, mock_getenv):
        mock_getenv.return_value = 'dummy_api_key'
        mock_response = Mock()
        mock_response.json.return_value = {
            "cod": "404"
        }
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            check_location('invalid_latitude', 'invalid_longitude')

if __name__ == '__main__':
    unittest.main()
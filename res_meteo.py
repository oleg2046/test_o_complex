import openmeteo_requests
import requests_cache
import pandas as pd
import numpy
from retry_requests import retry
from datetime import datetime, timedelta


def res_meteo(lat, lon, city):
	cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
	retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
	openmeteo = openmeteo_requests.Client(session=retry_session)

	url = "https://api.open-meteo.com/v1/forecast"
	params = {
		"latitude": lat,
		"longitude": lon,
		"hourly": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation_probability",
			"precipitation", "cloud_cover", "visibility", "wind_speed_10m"],
		"timezone": "auto"
	}
	responses = openmeteo.weather_api(url, params=params)

	response = responses[0]

	hourly = response.Hourly()
	hourly_temperature_2m = numpy.around(hourly.Variables(0).ValuesAsNumpy(), decimals=2 )
	hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
	hourly_apparent_temperature = hourly.Variables(2).ValuesAsNumpy()
	hourly_precipitation_probability = hourly.Variables(3).ValuesAsNumpy()
	hourly_precipitation = hourly.Variables(4).ValuesAsNumpy()
	hourly_cloud_cover = hourly.Variables(5).ValuesAsNumpy()
	hourly_visibility = hourly.Variables(6).ValuesAsNumpy()
	hourly_wind_speed_10m = hourly.Variables(7).ValuesAsNumpy()

	hourly_data = {"date": pd.date_range(
		start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
		end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
		freq=pd.Timedelta(seconds=hourly.Interval()),
		inclusive="left"
	), "temperature_2m": hourly_temperature_2m, "relative_humidity_2m": hourly_relative_humidity_2m,
		"apparent_temperature": hourly_apparent_temperature, "precipitation_probability": hourly_precipitation_probability,
		"precipitation": hourly_precipitation, "cloud_cover": hourly_cloud_cover, "visibility": hourly_visibility,
		"wind_speed_10m": hourly_wind_speed_10m}

	hourly_dataframe = pd.DataFrame(data=hourly_data)
	hourly_dataframe[['temperature_2m', 'apparent_temperature', 'wind_speed_10m']] = hourly_dataframe[['temperature_2m', 'apparent_temperature', 'wind_speed_10m']].map(round, ndigits=1)
	hourly_dataframe['date'] = pd.to_datetime(hourly_dataframe['date'])
	hourly_dataframe['city'] = city

	current_time = pd.Timestamp(datetime.utcnow(), tz='UTC')
	end_current_time = pd.Timestamp(datetime.utcnow() + timedelta(hours=5), tz='UTC')
	hourly_dataframe = hourly_dataframe[(hourly_dataframe['date'] >= current_time)
										& (hourly_dataframe['date'] <= end_current_time)]
	hourly_dataframe = hourly_dataframe.assign(index=['Сейчас', 'Через 1 час', 'Через 2 часа', 'Через 3 часа', 'Через 4 часа'])
	return hourly_dataframe.to_dict(orient='records')

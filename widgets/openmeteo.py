"""Widget: OpenMeteo"""

import openmeteo_requests
import pandas as pd
import pendulum

from retry_requests import retry

from templates import *
from .widget import *


__all__ = ["OpenMeteo"]


#
# OpenMeteo Widget
#
class OpenMeteo(Widget):
  """Fetch and parse Open-Meteo data."""

  CELCIUS = "celsius"
  FAHRENHEIT = "fahrenheit"

  ARGUMENTS = Widget.MAKE_ARGUMENTS(
    [
      ("latitude",  float),
      ("longitude", float),
      ("timezone",  str),
      ("units",     str,   CELCIUS),
      ("days",      int,   3),
      ("graph",     bool,  True),
      ("animation", bool,  True),
      ("min",       bool,  True),
      ("max",       bool,  True),
    ]
  )

  SCRIPT = True
  STYLES = True
  POST_FETCH = True
  URL_FORECAST = "https://api.open-meteo.com/v1/forecast"

  HAS_REQUESTS_SESSION = True
  REQUESTS_SESSION_CACHE_TIMEOUT = 3600

  def init(self):
    """Validate that we have a sane parameters."""

    required_params = ["latitude", "longitude", "timezone"]
    for param in required_params:
      v = self.params[param]
      if v is None:
        raise WidgetInitException(f"Missing '{param}' parameter. It is required.")

    days = self.params["days"]
    if days < 1 or days > 7:
      raise WidgetInitException(f"Invalid 'days' parameter. It must be between 1 and 7.")

    timezone = self.params["timezone"]
    try:
      pendulum.now(tz=timezone)
    except Exception:
      raise WidgetInitException(f"Invalid 'timezone' value specified: {timezone}")

    units = self.params["units"]
    if units not in (self.CELCIUS, self.FAHRENHEIT):
      raise WidgetInitException(f"Invalid 'units': {units}")

    # Setup the Open-Meteo API client with cache and retry on error
    req = self.get_requests()
    retry_session = retry(req, retries=5, backoff_factor=0.2)
    self.openmeteo_client = openmeteo_requests.Client(session=retry_session)

  def get_render_context_extras(self) -> dict:
    """Extra information for the template to use."""

    extras = {
      "chart_id": f"chart-{self.uniqueclass}"
    }

    return extras

  def fetch_data(self) -> dict:
    """Fetch and parse the Open-Meteo data."""

    latitude = self.params["latitude"]
    longitude = self.params["longitude"]
    timezone = self.params["timezone"]

    data = None
    if data is None:
      data0 = self._fetch_weather(latitude, longitude, timezone)
      if isinstance(data0, dict):
        data = {}
        extras = self.get_render_context_extras()
        if isinstance(extras, dict):
          data.update(**extras)
        data.update(**data0)

    return data

  def _jsdate(self, timestamp: int, tz: str) -> str:
    dt = pendulum.from_timestamp(timestamp, tz=tz).to_iso8601_string()
    return dt[:16]

  def _convert_df_datevalue_to_tsvalue(self, df: dict, date_field: str, value_field: str, tz: str):
    ts_dps = [
      (self._jsdate(date.timestamp(), tz), round(value, 1))
      for (_, date), (_, value) in zip(df[date_field].items(), df[value_field].items())
    ]

    return ts_dps

  def _get_current_tz(self) -> str:
    now = pendulum.now()
    return now.timezone_name

  def _fetch_weather(self, latitude: int | float, longitude: int | float, tz: str = None) -> dict | None:
    """Fetch and parse the weather data."""
    if tz is None:
      tz = self._get_current_tz()

    units = self.params["units"]
    units_str = "\u00b0" + ("F" if units == self.FAHRENHEIT else "C")

    weather_data = {}

    params = {
      "latitude": latitude,
      "longitude": longitude,
      "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "rain"],
      "timezone": tz,
      "forecast_days": self.params.days + 1 if self.params.graph else 1,
    }

    if self.params.graph:
      params.update({
        "hourly": ["temperature_2m", "precipitation", "precipitation_probability"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
      })

    if units == self.FAHRENHEIT:
      params["temperature_unit"] = units

    responses = self.openmeteo_client.weather_api(self.URL_FORECAST, params=params)

    if len(responses):
      response = responses[0]

      weather_data.update({
        "units": units_str,
        "current": self._get_current_data(response),
      })

      day_names = [
        pendulum.now(tz=tz).start_of("day").add(days=i).format("ddd")
        for i in range(params["forecast_days"])
      ]

      if self.params.graph:
        weather_data.update({
          "hourly": self._get_hourly_data(response, tz),
          "daily": self._get_daily_data(response, tz),
          "day_names": day_names,
        })

      return weather_data
    return None

  def _get_current_data(self, weather_response) -> dict:
    current = weather_response.Current()
    temperature = current.Variables(0).Value()
    relative_humidity = current.Variables(1).Value()
    apparent_temperature = current.Variables(2).Value()
    precipitation = current.Variables(3).Value()
    rain = current.Variables(4).Value()

    data = {
      "temperature": temperature,
      "relative_humidity": relative_humidity,
      "apparent_temperature": apparent_temperature,
      "precipitation": precipitation,
      "rain": rain,
    }

    return data

  def _get_hourly_data(self, weather_response, tz: str) -> dict:
    """Parse the hourly data from the response."""

    hourly = weather_response.Hourly()
    hourly_temperature = hourly.Variables(0).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()

    hourly_data = {
      "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end=pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq=pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
      )
    }

    hourly_data["temperature"] = hourly_temperature
    hourly_data["precipitation"] = hourly_precipitation
    hourly_dataframe = pd.DataFrame(data=hourly_data)

    # Remove last day, so that it matches with the daily data (this is
    # why we request an extra day to begin with).
    end_date = pendulum.from_timestamp(hourly.TimeEnd(), tz=tz).subtract(days=1)
    hourly_dataframe = hourly_dataframe[hourly_dataframe["date"] < end_date]

    dps_temperature = self._convert_df_datevalue_to_tsvalue(hourly_dataframe, "date", "temperature", tz=tz)
    dps_precipitation = self._convert_df_datevalue_to_tsvalue(hourly_dataframe, "date", "precipitation", tz=tz)

    now = pendulum.now(tz=tz)
    precip_cur = None
    precip_next = None

    for dt, value in dps_precipitation:
      precip_dt = pendulum.parse(dt, tz=tz)
      if value:
        minutes_since_precip = (now - precip_dt).total_minutes()
        if precip_cur is None and now > precip_dt and minutes_since_precip < 60:
          precip_cur = (self._jsdate(precip_dt.int_timestamp, tz=tz), value, minutes_since_precip)
        if precip_next is None and precip_dt > now:
          precip_next = (self._jsdate(precip_dt.int_timestamp, tz=tz), value, (precip_dt - now).total_minutes())

    data = {
      "temperature": dps_temperature,
      "precipitation": dps_precipitation,
      "precipitation_current": precip_cur,
      "precipitation_upcoming": precip_next,
    }

    return data

  def _get_daily_data(self, weather_response, tz: str) -> dict:
    """Parse the daily data from the response."""

    daily = weather_response.Daily()
    daily_temperature_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_min = daily.Variables(1).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(2).ValuesAsNumpy()

    daily_data = {
      "date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end=pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq=pd.Timedelta(seconds = daily.Interval()),
        inclusive="left"
      )
    }

    daily_data["temperature_max"] = daily_temperature_max
    daily_data["temperature_min"] = daily_temperature_min
    daily_data["precipitation_sum"] = daily_precipitation_sum

    daily_dataframe = pd.DataFrame(data=daily_data)

    dps_temperature_min = self._convert_df_datevalue_to_tsvalue(daily_dataframe, "date", "temperature_min", tz=tz)
    dps_temperature_max = self._convert_df_datevalue_to_tsvalue(daily_dataframe, "date", "temperature_max", tz=tz)
    dps_precipitation = self._convert_df_datevalue_to_tsvalue(daily_dataframe, "date", "precipitation_sum", tz=tz)

    data = {
      "temperature_min": dps_temperature_min,
      "temperature_max": dps_temperature_max,
      "precipitation": dps_precipitation,
    }

    return data

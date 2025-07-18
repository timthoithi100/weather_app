import requests
import datetime

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

def get_coordinates(city_name):
    params = {
        "name": city_name,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    try:
        response = requests.get(GEOCODING_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data and data.get('results'):
            result = data['results'][0]
            display_name = result.get('name')
            if result.get('admin1'):
                display_name += f", {result['admin1']}"
            if result.get('country'):
                display_name += f", {result['country']}"
            return result['latitude'], result['longitude'], display_name
        return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coordinates: {e}")
        return None, None, None

def get_weather_data(lat, lon, timezone="auto", daily_forecast_days=7):
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,showers,snowfall,weather_code,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
        "hourly": "temperature_2m,apparent_temperature,precipitation_probability,precipitation,rain,showers,snowfall,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m,wind_gusts_10m,uv_index",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,uv_index_max,precipitation_sum,precipitation_hours,precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max",
        "timezone": timezone,
        "forecast_days": daily_forecast_days + 1
    }
    air_quality_params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone",
        "timezone": timezone
    }
    try:
        weather_response = requests.get(OPEN_METEO_BASE_URL, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        air_quality_response = requests.get(OPEN_METEO_AIR_QUALITY_URL, params=air_quality_params)
        air_quality_response.raise_for_status()
        air_quality_data = air_quality_response.json()
        return weather_data, air_quality_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None, None

def get_weather_description(weather_code):
    descriptions = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog", 51: "Drizzle: Light",
        53: "Drizzle: Moderate", 55: "Drizzle: Dense intensity",
        56: "Freezing Drizzle: Light", 57: "Freezing Drizzle: Dense intensity",
        61: "Rain: Slight", 63: "Rain: Moderate", 65: "Rain: Heavy intensity",
        66: "Freezing Rain: Light", 67: "Freezing Rain: Heavy intensity",
        71: "Snow fall: Slight", 73: "Snow fall: Moderate",
        75: "Snow fall: Heavy intensity", 77: "Snow grains",
        80: "Rain showers: Slight", 81: "Rain showers: Moderate",
        82: "Rain showers: Violent", 85: "Snow showers: Slight",
        86: "Snow showers: Heavy", 95: "Thunderstorm: Slight or moderate",
        96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    return descriptions.get(weather_code, "Unknown weather")

def parse_weather_data(weather_data, air_pollution_data):
    if not weather_data:
        return None

    current_time_dt = datetime.datetime.fromisoformat(weather_data['current']['time'])
    
    hourly_times = [datetime.datetime.fromisoformat(t) for t in weather_data['hourly']['time']]
    current_hourly_index = min(range(len(hourly_times)), key=lambda i: abs(hourly_times[i] - current_time_dt))

    current_hourly_data = {k: v[current_hourly_index] for k, v in weather_data['hourly'].items() if k in ['temperature_2m', 'uv_index', 'precipitation_probability', 'rain', 'weather_code']}
    
    parsed_current = {
        "temp": weather_data['current'].get('temperature_2m'),
        "feels_like": weather_data['current'].get('apparent_temperature'),
        "humidity": weather_data['current'].get('relative_humidity_2m'),
        "description": get_weather_description(weather_data['current'].get('weather_code')),
        "weather_code": weather_data['current'].get('weather_code'),
        "uvi": current_hourly_data.get('uv_index'),
        "sunrise": datetime.datetime.fromisoformat(weather_data['daily']['sunrise'][0]) if weather_data['daily']['sunrise'] else None,
        "sunset": datetime.datetime.fromisoformat(weather_data['daily']['sunset'][0]) if weather_data['daily']['sunset'] else None,
        "rain_rate": weather_data['current'].get('precipitation'),
        "wind_speed": weather_data['current'].get('wind_speed_10m')
    }
    
    parsed_daily = []
    for i in range(len(weather_data['daily']['time'])):
        day_data = {k: v[i] for k, v in weather_data['daily'].items()}
        parsed_daily.append({
            "dt": datetime.datetime.fromisoformat(day_data['time']),
            "temp_max": day_data['temperature_2m_max'],
            "temp_min": day_data['temperature_2m_min'],
            "description": get_weather_description(day_data['weather_code']),
            "weather_code": day_data['weather_code'],
            "pop": day_data['precipitation_probability_max']
        })
    
    parsed_air_quality = None
    if air_pollution_data and air_pollution_data.get('hourly'):
        aq_hourly_times = [datetime.datetime.fromisoformat(t) for t in air_pollution_data['hourly']['time']]
        current_aq_index = min(range(len(aq_hourly_times)), key=lambda i: abs(aq_hourly_times[i] - current_time_dt))

        aq_components = {
            "pm10": air_pollution_data['hourly'].get('pm10', [None])[current_aq_index],
            "pm2_5": air_pollution_data['hourly'].get('pm2_5', [None])[current_aq_index],
            "co": air_pollution_data['hourly'].get('carbon_monoxide', [None])[current_aq_index],
            "no2": air_pollution_data['hourly'].get('nitrogen_dioxide', [None])[current_aq_index],
            "so2": air_pollution_data['hourly'].get('sulphur_dioxide', [None])[current_aq_index],
            "o3": air_pollution_data['hourly'].get('ozone', [None])[current_aq_index]
        }
        parsed_air_quality = {k: v for k, v in aq_components.items() if v is not None}
        if not parsed_air_quality:
            parsed_air_quality = None
            
    return {
        "current": parsed_current,
        "daily": parsed_daily,
        "air_quality": parsed_air_quality
    }
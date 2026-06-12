"""
Basit hava durumu ozeti — uzaktaki bir servis uzerinden calisir.
Kağan Yavuz tarafından yapılmıştır

Varsayilan konum:
- JARVIS_WEATHER_LOCATION env varsa onu kullanir
- yoksa Konya varsayilir
"""

from __future__ import annotations

import os

import requests


def get_weather_summary(location: str | None = None) -> str:
    target = (location or os.environ.get("JARVIS_WEATHER_LOCATION") or "Konya").strip()
    try:
        response = requests.get(
            f"https://wttr.in/{target}",
            params={"format": "j1"},
            timeout=10,
            headers={"User-Agent": "JARVIS Windows"},
        )
        response.raise_for_status()
        payload = response.json()
        current = (payload.get("current_condition") or [{}])[0]
        temp_c = current.get("temp_C")
        feels_like = current.get("FeelsLikeC")
        weather_desc = ((current.get("weatherDesc") or [{}])[0]).get("value", "")
        humidity = current.get("humidity")
        wind_speed = current.get("windspeedKmph")

        parts = []
        if temp_c:
            parts.append(f"{temp_c} derece")
        if weather_desc:
            parts.append(weather_desc.lower())
        if feels_like and feels_like != temp_c:
            parts.append(f"hissedilen {feels_like} derece")
        if humidity:
            parts.append(f"nem yüzde {humidity}")
        if wind_speed:
            parts.append(f"rüzgar {wind_speed} km/s")

        if not parts:
            return "Hava durumu bilgisi şu anda alınamadı."

        forecast = payload.get("weather", [])
        forecast_lines = []
        for idx, day in enumerate(forecast[:3]):
            date_label = "Bugün" if idx == 0 else "Yarın" if idx == 1 else "Ertesi gün"
            max_temp = day.get("maxtempC") or "?"
            min_temp = day.get("mintempC") or "?"
            desc = ""
            hourly = day.get("hourly") or []
            if hourly:
                preferred = hourly[min(4, len(hourly) - 1)]
                desc = ((preferred.get("weatherDesc") or [{}])[0]).get("value", "").lower()
            if not desc and day.get("avgtempC"):
                desc = f"ortalama {day.get('avgtempC')} derece"
            if desc:
                forecast_lines.append(f"{date_label}: {desc}, {max_temp}/{min_temp}°C")
            else:
                forecast_lines.append(f"{date_label}: {max_temp}/{min_temp}°C")

        forecast_text = " ".join(forecast_lines)
        return f"{target} için hava durumu: " + ", ".join(parts) + ". " + forecast_text + "."
    except Exception:
        return "Hava durumu bilgisi şu anda alınamadı."

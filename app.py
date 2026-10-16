import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta

st.set_page_config(
    page_title="AirWise India",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- MODERN DESIGN ----------
st.markdown("""
<style>
    .stApp { background: #f4f7fb; }
    [data-testid="stSidebar"] { background: #102a43; }
    [data-testid="stSidebar"] * { color: #f5f9ff !important; }
    .hero {
        padding: 1.6rem 1.8rem; border-radius: 22px;
        background: linear-gradient(120deg, #102a43, #087e8b);
        color: white; margin-bottom: 1.2rem;
    }
    .hero h1 { color: white; margin: 0; font-size: 2.1rem; }
    .hero p { color: #d9f4f4; margin-bottom: 0; }
    .small-note { color: #536579; font-size: 0.9rem; }
    div[data-testid="stMetric"] {
        background: white; padding: 1rem; border-radius: 16px;
        border: 1px solid #e4eaf1; box-shadow: 0 2px 10px #102a4308;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px;
    }
    h2, h3 { color: #102a43; }
    .status-good { background: #dcfce7; color: #166534; padding: 0.7rem 1rem; border-radius: 12px; }
    .status-warn { background: #fef3c7; color: #92400e; padding: 0.7rem 1rem; border-radius: 12px; }
    .status-bad { background: #fee2e2; color: #991b1b; padding: 0.7rem 1rem; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🌿 AirWise India</h1>
  <p>Air quality and weather, explained in simple language.</p>
</div>
""", unsafe_allow_html=True)

# Approximate coordinates for Indian cities; station coverage can vary.
CITY_COORDS = {
    "Jaipur": (26.9124, 75.7873),
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Lucknow": (26.8467, 80.9462),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Bengaluru": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Chandigarh": (30.7333, 76.7794),
    "Bhopal": (23.2599, 77.4126),
    "Indore": (22.7196, 75.8577),
    "Patna": (25.5941, 85.1376),
    "Bhubaneswar": (20.2961, 85.8245),
    "Amritsar": (31.6340, 74.8723),
    "Varanasi": (25.3176, 82.9739),
    "Nagpur": (21.1458, 79.0882),
}

# ---------- HISTORICAL DATA ----------
@st.cache_data
def load_data():
    df = pd.read_csv("city_day.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in ["AQI", "PM2.5", "PM10"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

st.sidebar.title("🧭 Explore dashboard")
page = st.sidebar.radio(
    "Go to",
    ["Overview", "Live air & weather", "About this project"],
)

if page == "Overview":
    try:
        df = load_data()
    except FileNotFoundError:
        st.error("city_day.csv must be in the same folder as app.py.")
        st.stop()

    if "City" not in df.columns or "Date" not in df.columns:
        st.error("Dataset must contain City and Date columns.")
        st.stop()

    st.sidebar.subheader("Historical filters")
    cities = sorted(df["City"].dropna().unique().tolist())
    selected_city = st.sidebar.selectbox("Choose a city", cities)
    valid_dates = df["Date"].dropna()
    if valid_dates.empty:
        st.error("No valid dates found in the dataset.")
        st.stop()

    min_date, max_date = valid_dates.min().date(), valid_dates.max().date()
    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    filtered = df[
        (df["Date"].dt.date >= start_date) &
        (df["Date"].dt.date <= end_date)
    ].copy()
    city_df = filtered[filtered["City"] == selected_city].sort_values("Date")

    st.subheader(f"📍 Historical overview · {selected_city}")
    st.caption("This section uses the historical CSV dataset, not live measurements.")

    metric_cols = st.columns(3)
    for i, metric in enumerate(["AQI", "PM2.5", "PM10"]):
        if metric in city_df.columns:
            values = city_df[metric].dropna()
            average = f"{values.mean():.1f}" if not values.empty else "No data"
            metric_cols[i].metric(f"Average {metric}", average)

    if "AQI" in city_df.columns:
        aqi_data = city_df.dropna(subset=["AQI"])
        if not aqi_data.empty:
            highest = aqi_data.loc[aqi_data["AQI"].idxmax()]
            st.info(
                f"Highest recorded AQI in this selected period: "
                f"{highest['AQI']:.1f} on {highest['Date'].strftime('%d %b %Y')}."
            )

    st.divider()
    st.subheader("📈 Pollution trends")
    pollutants = [
        c for c in ["AQI", "PM2.5", "PM10"]
        if c in city_df.columns and city_df[c].notna().any()
    ]
    if pollutants:
        selected_pollutants = st.multiselect(
            "Choose measurements", pollutants, default=pollutants
        )
        if selected_pollutants:
            trend = city_df.dropna(subset=["Date"]).set_index("Date")
            st.line_chart(trend[selected_pollutants])
    else:
        st.info("No pollutant readings for this city and date range.")

    st.divider()
    st.subheader("🏙️ Compare cities")
    if "AQI" in filtered.columns:
        comparison = (
            filtered.groupby("City", as_index=False)
            .agg(
                Average_AQI=("AQI", "mean"),
                Highest_AQI=("AQI", "max"),
                Days_Recorded=("AQI", "count"),
            )
            .dropna(subset=["Average_AQI"])
            .sort_values("Average_AQI", ascending=False)
        )
        if not comparison.empty:
            defaults = [
                c for c in ["Delhi", "Jaipur", "Mumbai"]
                if c in comparison["City"].tolist()
            ] or comparison["City"].head(3).tolist()
            chosen = st.multiselect(
                "Cities to compare", comparison["City"].tolist(), default=defaults
            )
            view = comparison[comparison["City"].isin(chosen)]
            if not view.empty:
                st.bar_chart(view.set_index("City")[["Average_AQI"]])
                st.dataframe(view.round(2), width="stretch", hide_index=True)
        else:
            st.info("No AQI data for this date range.")

    st.divider()
    st.subheader("🧪 Average pollutant levels")
    pollutant_columns = [c for c in ["PM2.5", "PM10"] if c in filtered.columns]
    if pollutant_columns:
        summary = filtered.groupby("City")[pollutant_columns].mean().round(2)
        st.bar_chart(summary)
    else:
        st.info("PM2.5 and PM10 columns are not available.")

    st.download_button(
        "📥 Download filtered CSV report",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="air_quality_report.csv",
        mime="text/csv",
    )

elif page == "Live air & weather":
    st.subheader("🌏 Live air quality and local weather")
    st.write("Choose a city to check nearby monitoring stations and current weather.")
    try:
        api_key = st.secrets.get("OPENAQ_API_KEY", "")
    except Exception:
        api_key = ""

    city = st.selectbox("Choose a city", list(CITY_COORDS.keys()), key="live_city")
    lat, lon = CITY_COORDS[city]
    left, right = st.columns(2)

    @st.cache_data(ttl=600)
    def get_locations(city_name, latitude, longitude, key):
        response = requests.get(
            "https://api.openaq.org/v3/locations",
            headers={"X-API-Key": key},
            params={
                "coordinates": f"{latitude},{longitude}",
                "radius": 25000,
                "limit": 100,
                "iso": "IN",
            },
            timeout=20,
        )
        response.raise_for_status()
        return response.json().get("results", [])

    @st.cache_data(ttl=300)
    def get_latest(location_id, key):
        response = requests.get(
            f"https://api.openaq.org/v3/locations/{location_id}/latest",
            headers={"X-API-Key": key},
            params={"limit": 100},
            timeout=20,
        )
        response.raise_for_status()
        return response.json().get("results", [])

    @st.cache_data(ttl=300)
    def get_weather(latitude, longitude):
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    weather_labels = {
        0: "Clear sky", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Fog", 51: "Light drizzle", 53: "Drizzle",
        55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
        71: "Light snow", 80: "Rain showers", 81: "Rain showers",
        82: "Heavy rain showers", 95: "Thunderstorm", 96: "Thunderstorm",
        99: "Thunderstorm",
    }

    try:
        with st.spinner("Getting current weather..."):
            weather = get_weather(lat, lon)
        current = weather.get("current", {})
        with right:
            st.markdown("#### 🌤️ Weather now")
            w1, w2 = st.columns(2)
            w1.metric("Temperature", f"{current.get('temperature_2m', '—')} °C")
            w2.metric("Feels like", f"{current.get('apparent_temperature', '—')} °C")
            w3, w4 = st.columns(2)
            w3.metric("Humidity", f"{current.get('relative_humidity_2m', '—')}%")
            w4.metric("Wind speed", f"{current.get('wind_speed_10m', '—')} km/h")
            code = current.get("weather_code")
            st.caption(f"{weather_labels.get(code, 'Weather conditions')}")
            st.caption(f"Weather observation time: {current.get('time', 'not provided')} (local city time)")
    except requests.exceptions.RequestException:
        with right:
            st.warning("Weather data is temporarily unavailable. Please retry.")

    with left:
        st.markdown("#### 🌫️ Air quality stations")
        if not api_key:
            st.warning("OpenAQ API key missing. Add OPENAQ_API_KEY to .streamlit/secrets.toml.")
            st.stop()

        if st.button("🔄 Refresh live data"):
            get_locations.clear()
            get_latest.clear()
            get_weather.clear()
            st.rerun()

        try:
            with st.spinner("Searching nearby stations..."):
                locations = get_locations(city, lat, lon, api_key)

            if not locations:
                st.info("No stations found within 25 km. Try another city.")
            else:
                def station_label(loc):
                    name = loc.get("name") or loc.get("locality") or "Unnamed station"
                    return f"{name} · ID {loc.get('id')}"

                station_map = {station_label(loc): loc for loc in locations}
                station_label_selected = st.selectbox(
                    "Monitoring station", list(station_map.keys())
                )
                station = station_map[station_label_selected]
                readings = get_latest(station["id"], api_key)

                # Sensor metadata may be included in location or latest response.
                sensor_map = {}
                for sensor in station.get("sensors", []):
                    sensor_map[sensor.get("id")] = sensor
                for item in readings:
                    sensor = item.get("sensors") or item.get("sensor") or {}
                    if isinstance(sensor, dict) and sensor.get("id"):
                        sensor_map[sensor["id"]] = sensor

                rows = []
                now_utc = datetime.now(timezone.utc)
                for item in readings:
                    sensor_id = item.get("sensorsId") or item.get("sensorId")
                    sensor = sensor_map.get(sensor_id, {})
                    parameter = sensor.get("parameter", {}) if isinstance(sensor, dict) else {}
                    parameter_name = (
                        parameter.get("displayName")
                        or parameter.get("name")
                        or item.get("parameter", {}).get("name")
                        or "Pollutant"
                    )
                    unit = parameter.get("units") or item.get("parameter", {}).get("units") or ""
                    dt_obj = None
                    date_info = item.get("datetime", {})
                    raw_time = date_info.get("utc") if isinstance(date_info, dict) else None
                    if raw_time:
                        try:
                            dt_obj = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
                            if dt_obj.tzinfo is None:
                                dt_obj = dt_obj.replace(tzinfo=timezone.utc)
                        except ValueError:
                            dt_obj = None
                    age_hours = (now_utc - dt_obj.astimezone(timezone.utc)).total_seconds() / 3600 if dt_obj else None
                    if age_hours is None:
                        freshness = "Time unavailable"
                    elif age_hours <= 24:
                        freshness = "Recent (within 24h)"
                    elif age_hours <= 168:
                        freshness = "Older (1–7 days)"
                    else:
                        freshness = "Stale (over 7 days)"
                    rows.append({
                        "Pollutant": str(parameter_name),
                        "Value": item.get("value"),
                        "Unit": unit,
                        "Measured at (UTC)": raw_time or "Not provided",
                        "Freshness": freshness,
                        "_age_hours": age_hours,
                    })

                if rows:
                    live_df = pd.DataFrame(rows)
                    st.caption(
                        f"Station: {station.get('name') or station.get('locality') or 'Unnamed station'}"
                    )

                    recent_rows = live_df[
                        live_df["_age_hours"].notna()
                        & (live_df["_age_hours"] <= 24)
                    ]

                    show_old = st.checkbox(
                        "Show older measurements too",
                        value=False,
                        key="show_old_measurements",
                    )

                    if recent_rows.empty:
                        st.warning(
                            "No measurements from the last 24 hours are available "
                            "at this station. Try another city or station."
                        )
                        st.info(
                            "Older measurements are hidden by default so they are "
                            "not mistaken for current pollution levels."
                        )
                    else:
                        st.success(
                            f"{len(recent_rows)} measurement(s) found from the last 24 hours."
                        )

                    display_rows = live_df if show_old else recent_rows

                    if not display_rows.empty:
                        st.dataframe(
                            display_rows.drop(columns=["_age_hours"]),
                            width="stretch",
                            hide_index=True,
                        )

                    st.caption(
                        "Source: OpenAQ. Measurements are not necessarily an official AQI. "
                        "Times are shown in UTC."
                    )

                    # Plain-language explainer for common pollutants
                    st.markdown("#### 💡 What do these readings mean?")
                    explanations = {
                        "pm2.5": (
                            "PM2.5 means very tiny particles that can travel deep into the lungs. "
                            "Reducing smoke, dust, and heavy outdoor exertion can help limit exposure."
                        ),
                        "pm10": (
                            "PM10 includes larger airborne particles such as dust. If dust levels "
                            "are high, consider reducing time near dusty roads or construction."
                        ),
                        "no2": (
                            "Nitrogen dioxide (NO₂) is a gas often linked to traffic and combustion. "
                            "Busy roads can be a source of exposure."
                        ),
                        "o3": (
                            "Ground-level ozone (O₃) can irritate the lungs, especially during outdoor "
                            "activity. Follow local health advisories when ozone is elevated."
                        ),
                        "so2": (
                            "Sulfur dioxide (SO₂) is a gas that can irritate the respiratory system. "
                            "People with asthma may be more sensitive."
                        ),
                        "co": (
                            "Carbon monoxide (CO) is a gas produced by incomplete combustion. "
                            "Its health meaning depends on the unit and concentration, so check the "
                            "measurement unit and local guidance."
                        ),
                    }

                    for _, row in display_rows.iterrows():
                        pollutant_key = str(row["Pollutant"]).lower().replace("₂", "2").replace("₃", "3")
                        for key, explanation in explanations.items():
                            if key in pollutant_key:
                                st.markdown(f"**{row['Pollutant']}** — {explanation}")
                                break

                    # Practical health guidance based on pollutant names and measurement freshness.
                    # This intentionally does not convert a single reading into an official AQI.
                    st.markdown("#### 🩺 Health guidance")
                    recent_pollutants = display_rows.copy()
                    recent_pollutants["_pollutant_key"] = recent_pollutants["Pollutant"].astype(str).str.lower().str.replace("₂", "2").str.replace("₃", "3")
                    found_pm25 = recent_pollutants[recent_pollutants["_pollutant_key"].str.contains("pm2.5|pm25", regex=True)]
                    found_pm10 = recent_pollutants[recent_pollutants["_pollutant_key"].str.contains("pm10", regex=True)]
                    found_gases = recent_pollutants[recent_pollutants["_pollutant_key"].str.contains("no2|o3|so2|co", regex=True)]

                    if recent_rows.empty and not show_old:
                        st.warning("No reading from the last 24 hours is available for this station. Choose another station or refresh before making decisions based on current conditions.")
                    else:
                        st.markdown("**General precautions you can use:**")
                        advice = []
                        for _, measurement in found_pm25.iterrows():
                            try:
                                value = float(measurement["Value"])
                            except (TypeError, ValueError):
                                continue
                            unit = str(measurement["Unit"]).lower().replace("µ", "u").replace("μ", "u")
                            if "ug/m" in unit or "microgram" in unit:
                                if value > 35:
                                    advice.append("PM2.5 reading is elevated: consider reducing prolonged or strenuous outdoor activity, especially for children, older adults, and people with heart or lung conditions.")
                                elif value > 15:
                                    advice.append("PM2.5 is above a low reference level: sensitive people may prefer lighter outdoor activity and should follow local air-quality advisories.")
                                else:
                                    advice.append("The reported PM2.5 value is relatively low against the simple reference used here, but one station reading does not guarantee clean air everywhere.")
                        for _, measurement in found_pm10.iterrows():
                            try:
                                value = float(measurement["Value"])
                            except (TypeError, ValueError):
                                continue
                            unit = str(measurement["Unit"]).lower().replace("µ", "u").replace("μ", "u")
                            if "ug/m" in unit or "microgram" in unit:
                                if value > 100:
                                    advice.append("PM10 reading is elevated: avoid dusty roads and construction areas where possible; consider limiting strenuous activity outdoors.")
                                elif value > 45:
                                    advice.append("PM10 is above a low reference level: reduce exposure to dust where practical, especially if you are sensitive to it.")
                        if found_gases.shape[0] > 0:
                            advice.append("For gas readings (NO₂, O₃, SO₂, or CO), interpretation depends strongly on units and averaging period. Check local official advisories rather than using this dashboard alone to judge risk.")
                        if advice:
                            for item in dict.fromkeys(advice):
                                st.markdown(f"- {item}")
                        else:
                            st.info("No supported PM2.5/PM10 concentration with a recognizable unit was available for simple guidance. Check the station timestamp, units, and local official advisory.")

                    st.caption("These are cautious, general exposure tips—not medical advice or an official AQI/health-risk classification. Reference comparisons are only indicative and are not valid substitutes for 24-hour averages or local standards.")

                    st.info(
                        "These are general explanations, not a diagnosis or an official AQI category. "
                        "Pollutant values must be interpreted with their units, timestamp, and local guidance."
                    )
                else:
                    st.info("This station has no latest readings available.")
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "unknown"
            if status == 401:
                st.error("OpenAQ API key invalid or unauthorized. Check secrets.toml (do not share your key).")
            elif status == 429:
                st.error("OpenAQ request limit reached. Wait a little and retry.")
            else:
                st.error(f"OpenAQ API returned HTTP {status}.")
        except requests.exceptions.RequestException:
            st.error("Could not connect to OpenAQ. Check your internet connection.")
        except (KeyError, TypeError, ValueError) as exc:
            st.error(f"Could not read the station response: {exc}")

else:
    st.subheader("About AirWise India")
    st.write(
        "AirWise India combines a historical pollution dataset with current weather "
        "and available monitoring-station measurements. Historical data and live data "
        "are shown separately so older records are not mistaken for current conditions."
    )
    st.markdown("""
    - **PM2.5:** Very tiny particles that can travel deep into the lungs.
    - **PM10:** Larger airborne particles such as dust.
    - **AQI:** An index used by official agencies to communicate air pollution levels.
    - **Measurement time matters:** A value from an old timestamp may not describe today's air.
    """)
    st.info(
        "This dashboard does not calculate an official AQI from individual pollutant readings. "
        "Use local public-health guidance for decisions about sensitive health conditions."
    )

st.divider()
st.caption("AirWise India · Historical pollution data, monitoring-station readings, and weather shown separately.")

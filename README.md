# AirWise India 🌿

A beginner-friendly Streamlit dashboard for exploring historical air-pollution trends, available monitoring-station readings, and current weather for Indian cities.

## Features

- Historical pollution dashboard with city/date filters
- AQI, PM2.5 and PM10 trend charts
- City comparison and average pollutant summaries
- CSV download for filtered historical data
- OpenAQ monitoring-station readings with measurement freshness labels
- Current weather from Open-Meteo (no weather API key required)
- Plain-language pollutant explanations and cautious general health guidance
- About page describing data limitations

## Project files

- `app.py` — Streamlit application
- `city_day.csv` — small **demo dataset** so the project opens immediately
- `requirements.txt` — Python packages
- `.streamlit/secrets.toml.example` — example OpenAQ key configuration

## Run on Windows (VS Code)

1. Extract this ZIP into a folder, for example `AirWiseIndia`.
2. Open that folder in VS Code.
3. Open **Terminal → New Terminal**.
4. (Recommended) Create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

5. Install packages:

   ```powershell
   python -m pip install -r requirements.txt
   ```

6. Start the dashboard:

   ```powershell
   python -m streamlit run app.py
   ```

7. Streamlit will show a local URL, usually `http://localhost:8501`.

## Enable live OpenAQ readings

Live weather works without an API key. To enable OpenAQ station data:

1. Obtain your own API key from OpenAQ.
2. In the project folder, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
3. Open `secrets.toml` and replace `paste_your_own_key_here` with your key.
4. Save and restart Streamlit.

Never share or commit `secrets.toml`. It is excluded by `.gitignore`.

## Historical dataset note

The included `city_day.csv` is a **small illustrative demo dataset**, not a complete official historical record. For a real analysis or hackathon submission, replace it with the full dataset you are licensed to use. Keep the filename `city_day.csv` and ensure it includes at least `City`, `Date`, `AQI`, `PM2.5`, and `PM10` columns (missing pollutant columns are handled where possible).

## Important limitations

- OpenAQ station coverage varies by city; some locations may have no readings from the last 24 hours.
- OpenAQ pollutant measurements are not automatically an official AQI score.
- Health guidance is general and cautious, not medical advice. Check local official advisories for decisions.
- Historical demo values are illustrative and must not be presented as live observations.

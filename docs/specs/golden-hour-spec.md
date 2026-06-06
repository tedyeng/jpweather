# Spec: Golden & Blue Hour Feature (jpweather)

## Objective
Provide photographers and outdoor enthusiasts with exact start and end times for Golden Hour and Blue Hour, combined with real-time and forecast hourly weather conditions (cloud cover, precipitation probability) to determine the best times for photography.

### User Stories
1. **On-demand Query**: As a photographer, I want to type `jpweather golden "Tokyo"` to quickly check today's sunrise/sunset Golden & Blue hour windows, along with a rating of how good the shooting conditions will be.
2. **Weekly Planning**: As a landscape photographer, I want to type `jpweather golden "Kyoto" --week` to see a table of the upcoming week's morning/evening light windows to plan my travel.
3. **Mobile Screen Viewing**: As a mobile user ssh-ing from my phone, I want to run the command with `--mobile` to see a compact, single-screen-friendly layout without broken border lines.

---

## Tech Stack
*   **Language**: Python >= 3.10
*   **Key Dependencies**:
    *   `requests` (v2.34.2) - API requests to Open-Meteo and OSM.
    *   `rich` (v15.0.0) - Beautiful terminal printing and styling.
    *   `click` (v8.4.1) - Command-line interface definition.
    *   `questionary` (v2.1.1) - Interactive prompt fallback when no location is provided.
*   **Astronomy Logic**: Pure Python implementation of the SunCalc algorithm (computing solar declination, hour angle, and transit times locally).

---

## Commands
*   **Interactive Guide**: `uv run jpweather` (will include "Golden Hour" option in menu)
*   **Today's Golden Hour**: `uv run jpweather golden "Tokyo"`
*   **Weekly Golden Hour**: `uv run jpweather golden "Tokyo" --week`
*   **Mobile Mode**: `uv run jpweather golden "Tokyo" --mobile`
*   **Non-Interactive (Script-friendly)**: `uv run jpweather golden "Tokyo" --no-interactive`
*   **Run Unit Tests**: `uv run pytest`

---

## Project Structure
We will introduce a new module for sun calculation and integrate it into the existing CLI and API layers:

```
src/jpweather/
├── __init__.py
├── api.py           # Modified: added hourly weather fetching for golden hours
├── cache.py         # Handles sqlite caching for geocoding & weather forecasts
├── cli.py           # Modified: added the 'golden' sub-command
├── formatter.py     # Modified: added rendering logic for golden hour CLI layouts
└── suncalc.py       # New: Solar math helper (pure Python translation of SunCalc)

tests/
├── test_jpweather.py
├── test_weather_enhancements.py
├── test_suncalc.py  # New: Unit tests for solar math verification
└── test_golden.py   # New: Unit tests for golden CLI command integration
```

---

## Code Style
We follow the type-hinted, clean standard Python pattern used in the codebase.
Here is an example code structure for the new `suncalc.py`:

```python
import math
from datetime import datetime, timezone
from typing import Dict, Tuple

# Solar Constants
RAD = math.pi / 180.0
ECLIPTIC_OBLIQUITY = 23.4397 * RAD

def get_julian_date(date: datetime) -> float:
    """Calculate Julian Date from datetime object."""
    # Convert to UTC first
    utc_dt = date.astimezone(timezone.utc)
    time_ms = utc_dt.timestamp() * 1000.0
    return (time_ms / 86400000.0) + 2440587.5

def get_solar_declination(julian_days: float) -> float:
    """Compute solar declination angle in radians."""
    # Mean anomaly
    g = (357.5291 + 0.98560028 * julian_days) * RAD
    # Ecliptic longitude
    q = (280.459 + 0.98564736 * julian_days) * RAD
    l = q + (1.9148 * math.sin(g) + 0.02 * math.sin(2 * g) + 0.0003 * math.sin(3 * g)) * RAD
    return math.asin(math.sin(l) * math.sin(ECLIPTIC_OBLIQUITY))
```

---

## Testing Strategy
*   **Framework**: `pytest`
*   **Locations for Mock Data**: We will mock all API HTTP responses in `tests/test_golden.py` using `unittest.mock.patch`.
*   **Astronomy Validation**:
    *   Verify calculated sunrise and sunset times in `test_suncalc.py` against standard meteorological observations (e.g., Tokyo, London, Taipei) on specific equinox/solstice dates.
    *   Allow a maximum margin of error of $\pm 2$ minutes compared to official astronomical calculators (e.g., NOAA solar calculator).
*   **CLI Integration**:
    *   Test correct output formatting and `--mobile` layout constraints.
    *   Ensure proper timezone shifts are applied to UTC timestamps calculated by `suncalc.py`.

---

## Boundaries
*   **Always do**:
    *   Ensure all calculated times are localized using the timezone returned by Open-Meteo (e.g. `Asia/Tokyo`).
    *   Use the existing local SQLite caching system (`cache.py`) to prevent redundant Geocoding and Weather requests.
    *   Follow PEP 8 styling and maintain CJK double-width formatting alignment in terminals.
*   **Ask first**:
    *   Adding new Python library dependencies (e.g., `pytz`, `astral`, or `numpy`). We aim for zero external math dependencies.
*   **Never do**:
    *   Use native Python `datetime.now()` without timezone info (always use timezone-aware datetimes).
    *   Skip writing unit tests for the sun coordinate math.

---

## Success Criteria

### 1. Solar Math Precision
*   `get_sun_times(latitude, longitude, date)` resolves:
    *   **Blue Hour (Morning)**: Sun angle between $-6^\circ$ and $-4^\circ$.
    *   **Golden Hour (Morning)**: Sun angle between $-4^\circ$ and $6^\circ$.
    *   **Golden Hour (Evening)**: Sun angle between $6^\circ$ and $-4^\circ$.
    *   **Blue Hour (Evening)**: Sun angle between $-4^\circ$ and $-6^\circ$.
*   Comparison with NOAA solar data exhibits a differences of $\le 2$ minutes.

### 2. Smart Weather Rating Logic
We evaluate the shooting conditions by matching the computed golden/blue hour intervals with Open-Meteo's hourly weather forecast:
*   **Parameters Checked**: Cloud Cover (`cloud_cover` %), Precipitation Probability (`precipitation_probability` %), and Weather Code (`weather_code`).
*   **Rating Rules**:
    *   🌧️ **Rain/Snow (Precipitation > 30% or Weather Code indicates rain/snow)**: ⭐ (1 Star) - *“Rainy/Snowy. Not recommended for photography.”*
    *   ☁️ **Heavy Cloud (Cloud Cover > 90%)**: ⭐⭐ (2 Stars) - *“Overcast. Light will be blocked.”*
    *   ⛅ **Partly Cloudy (Cloud Cover between 30% and 70%)**: ⭐⭐⭐⭐⭐ (5 Stars) - *“Perfect shooting conditions! Ideal for vibrant twilight skies and crepuscular rays.”*
    *   ☀️ **Clear Skies (Cloud Cover < 10%)**: ⭐⭐⭐⭐ (4 Stars) - *“Clear sky. Soft warm light, but sky might lack dramatic clouds.”*
    *   Other ranges scale between 3 and 4 stars appropriately.

### 3. Display alignment & CJK handling
*   Output uses standard `Rich` layout boxes with clean labels:
    *   `Golden Hour (Evening)` labeled in yellow/gold.
    *   `Blue Hour (Evening)` labeled in deep blue/cyan.
*   `--mobile` restricts layout strictly to 38 column width without line wrapping or box misalignment on terminals.
*   `--week` produces a clean 7-row table showing Date, Day, Blue Hour (AM), Golden Hour (AM), Golden Hour (PM), Blue Hour (PM), and Rating.

---

## Open Questions
*   Should the CLI support passing a specific date (e.g., `--date 2026-06-10`) in addition to `--week`? (Recommend: Keep it simple for MVP. Default is today, and `--week` covers the next 7 days).

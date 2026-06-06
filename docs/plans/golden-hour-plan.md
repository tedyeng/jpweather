# Implementation Plan: Golden & Blue Hour Feature

## Overview
This plan outlines the technical design, tasks, and verification checkpoints to introduce the `golden` command into `jpweather`. The command displays precise Golden Hour and Blue Hour start/end times and calculates a Photography Recommendation Index using Open-Meteo's hourly cloud cover and precipitation forecasts.

---

## Architecture Decisions
1. **Local Solar Mathematics (`suncalc.py`)**:
   We will implement a lightweight, pure Python module `suncalc.py` to calculate the sun transit, sunrise, sunset, and times for custom solar elevations ($-6^\circ$, $-4^\circ$, $6^\circ$). This avoids heavy dependencies like `astral` and eliminates runtime overhead.
2. **API Data Expansion**:
   We will extend the `api.py` query to fetch Open-Meteo's hourly forecast parameters (`cloud_cover`, `precipitation_probability`, `weather_code`). The geocoding query resolves coordinates and local timezone, which are fed into `suncalc.py` to calculate solar times in UTC, then shifted into local time using standard library zoneinfo or simple offset shifts.
3. **Photography Rating Algorithm**:
   We will evaluate the weather metrics matching each golden/blue hour window. An average cloud cover and precipitation probability during the 30-60 minute window will define the star rating (1 to 5 stars) and a recommended shooting guideline.
4. **Rich Console Display**:
   We will add CLI commands and visual layouts inside `formatter.py` and `cli.py`, conforming to existing double-width CJK alignments and the 38-column `--mobile` mode constraint.

---

## Task List

### Phase 1: Foundation (Solar Calculations)

#### Task 1: Create `suncalc.py` Module
* **Description**: Write pure Python methods to compute Julian days, solar declination, transit times, and specific elevation angle times.
* **Acceptance criteria**:
  - `get_julian_date(date)` returns correct fractional Julian Day.
  - `get_sun_times(lat, lon, date)` returns exact datetime objects for:
    - Sunrise & Sunset (elevation $-0.833^\circ$)
    - Blue Hour boundaries (morning/evening, elevations $-6^\circ$ to $-4^\circ$)
    - Golden Hour boundaries (morning/evening, elevations $-4^\circ$ to $6^\circ$)
* **Verification**:
  - Write unit tests in `tests/test_suncalc.py` checking computed sunrise/sunset times against NOAA solar calculations for Tokyo and London on equinoxes (March 20, Sept 22) and solstices (June 21, Dec 21) in 2026. Tolerance: $\le 2$ minutes.
* **Dependencies**: None
* **Files likely touched**:
  - `src/jpweather/suncalc.py`
  - `tests/test_suncalc.py`
* **Estimated scope**: Medium (2 files)

---

### Checkpoint: Foundation
- [ ] `pytest tests/test_suncalc.py` passes successfully.
- [ ] No external dependencies added to `pyproject.toml` for math logic.

---

### Phase 2: API & Integration

#### Task 2: Update `api.py` for Hourly Weather Retrieval
* **Description**: Modify the weather API fetch to request hourly parameters (`cloud_cover`, `precipitation_probability`, `weather_code`) from Open-Meteo, allowing our CLI to fetch forecast conditions for the golden/blue hour windows.
* **Acceptance criteria**:
  - `api.get_weather` accepts hourly parameters or always fetches them.
  - Correctly extracts hourly array lists.
  - Database caching (`cache.py`) handles the updated JSON structure properly.
* **Verification**:
  - Run `pytest tests/test_weather_enhancements.py` and ensure previous weather calls still pass.
  - Verify that mock weather APIs reflect hourly values.
* **Dependencies**: Task 1
* **Files likely touched**:
  - `src/jpweather/api.py`
  - `tests/test_weather_enhancements.py`
* **Estimated scope**: Small (2 files)

#### Task 3: Implement Photography Index Calculator
* **Description**: Create a function to calculate the photography index (1 to 5 stars) and text recommendation by matching computed sun windows with hourly weather parameters.
* **Acceptance criteria**:
  - Correctly computes average cloud cover and precipitation probability for a datetime window (e.g. 17:45 - 18:25).
  - Emits 5 stars for partly cloudy (30-70% clouds), 4 stars for clear (<10%), 2 stars for heavy overcast (>90%), and 1 star for rain/snow.
* **Verification**:
  - Create tests in a new file `tests/test_golden.py` validating rating logic against various cloud/rain conditions.
* **Dependencies**: Task 2
* **Files likely touched**:
  - `src/jpweather/api.py` (or a helper in `formatter.py`)
  - `tests/test_golden.py`
* **Estimated scope**: Small (2 files)

---

### Checkpoint: Core Features
- [ ] All tests in `tests/` pass.
- [ ] The core calculator can fetch coordinate local times, solar angles, and return correct weather ratings.

---

### Phase 3: CLI & Formatting

#### Task 4: Visual Formatting in `formatter.py`
* **Description**: Implement formatting tables for the `golden` command, including the single-day summary card, the 7-day forecast table (`--week`), and their respective `--mobile` (38-column) compact versions.
* **Acceptance criteria**:
  - Render beautiful `Rich` tables using gold/yellow colors for Golden Hour and blue/cyan for Blue Hour.
  - Adjust margins and column widths under `--mobile` to avoid CJK truncation or broken lines.
* **Verification**:
  - Review rendering outputs locally using mockup visual testing or printing.
* **Dependencies**: Task 3
* **Files likely touched**:
  - `src/jpweather/formatter.py`
* **Estimated scope**: Small (1 file)

#### Task 5: Add CLI `golden` Subcommand and wizard option
* **Description**: Add the `@click.command("golden")` in `cli.py`, parsing location, `--week`, and `--mobile` options. Also integrate this option as menu item `4` in the interactive wizard list.
* **Acceptance criteria**:
  - Typing `jpweather golden "東京"` displays today's table.
  - Interactive wizard option "4" triggers the golden layout.
  - Handles timezone conversions to localized local time of the queried coordinate.
* **Verification**:
  - Manually run `uv run jpweather golden "Tokyo"` and check output alignment.
  - Run `uv run pytest` to ensure zero regressions across CLI tests.
* **Dependencies**: Task 4
* **Files likely touched**:
  - `src/jpweather/cli.py`
  - `tests/test_golden.py`
* **Estimated scope**: Small (2 files)

---

### Checkpoint: Complete
- [ ] CLI runs correctly.
- [ ] Automated tests cover `suncalc.py`, `api.py` modifications, and `cli.py` commands.
- [ ] Review formatting with human.

---

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Underflows/Overflows in Trigonometry | High | Bound $\cos(H)$ values to $[-1, 1]$ before passing to `acos` to prevent domain errors (Polar regions / extreme latitudes). |
| Timezone Library mismatch | Medium | Open-Meteo returns location timezone string. We will use standard `zoneinfo.ZoneInfo` (Python 3.9+) to localize time objects safely. |
| DB Cache stale structure | Medium | If user already has cached weather objects without hourly parameters, API might crash. Mitigation: if hourly variables are absent in cache, fallback to fresh API fetch or catch KeyError cleanly. |

## Open Questions
- None (resolved: MVP will focus strictly on today and `--week`).

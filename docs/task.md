# Tasks

- [x] Initialize Python project with `uv`
- [x] Add dependencies (`click`, `requests`, `rich`, `questionary`, `platformdirs`)
- [x] Implement geocoding & JMA weather API client (`src/jpweather/api.py`)
- [x] Implement SQLite caching mechanism (`src/jpweather/cache.py`)
- [x] Implement terminal formatting, custom WMO emoji mapping, and UI layout (`src/jpweather/formatter.py`)
- [x] Implement CLI commands, click controller, and interactive wizard (`src/jpweather/cli.py`)
- [x] Configure `pyproject.toml` console script entry point
- [x] Verify the application by running command lines
- [x] Create base unit tests and run them (`tests/test_jpweather.py`)
- [x] Implement OpenStreetMap Nominatim fallback geocoding for tourist spots and mountains (e.g. "上高地")
- [x] Implement 3-hourly weather forecast block table (Next 24h) under current weather
- [x] Support smart CJK 3-character administrative suffix handling and variation matching
- [x] Implement robust error handling (avoiding uncaught exceptions on network failure) and cache failure protection
- [x] Create additional test suites for error handling, CJK 3-character matching, and cache reliability (`tests/test_weather_enhancements.py`)
- [x] Implement decimal and DMS (Degrees, Minutes, Seconds) GPS coordinate parsing and format sanitization (e.g. CJK/English formats)
- [x] Integrate OpenStreetMap Nominatim reverse geocoding to resolve GPS coordinates to CJK place names
- [x] Create unit tests for GPS parsing, Nominatim reverse geocoding, and network fallbacks
- [x] Generate and keep walkthrough updated (`walkthrough.md`)
- [x] Update and synchronize all project documentation and README files

## Mobile Layout Feature Integration
- [x] Modify `src/jpweather/cli.py` to support `--mobile` options and adjust `--help` alignments
- [x] Add unit tests in `tests/test_weather_enhancements.py` for mobile output formatting
- [x] Update `README.md` and documentation
- [x] Verify functionality via CLI tests

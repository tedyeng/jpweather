# Changelog

All notable changes to the `jpweather` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---
## [0.2.1] - 2026-06-06

### Fixed
- **Missing Import NameError**: Fixed a crash (`NameError: name 'Optional' is not defined`) in `formatter.py` by properly importing `Optional` from the `typing` library.
- **Rendering Integration Test**: Added a new unit test suite to execute and validate all rendering outputs under today, week, mobile, and polar layout formats to prevent future runtime name errors.

---

## [0.2.0] - 2026-06-06

### Added
- **Golden & Blue Hour Feature**: Added a new command `golden` to calculate morning/evening Golden and Blue Hour起訖 times based on native solar astronomy equations (`suncalc.py`).
- **Photography Rating System**: Integrated Open-Meteo forecasts (cloud cover, precipitation probability, weather codes) to evaluate photography conditions with a 1-to-5 star rating and localized recommendations.
- **Polar Day / Polar Night Support**: Automatically detects when a coordinate is experiencing a polar day or polar night and displays clean warning panels instead of blank times.
- **Dynamic Responsive UI**: Implemented layout detection in daily view. If the terminal width is less than 112 columns, cards stack vertically to avoid squeezing or text wrapping; otherwise, they display side-by-side.
- **Standard Logging**: Configured a `logging` framework in `api.py` to replace silent exception catches, improving developer debugging.
- **Fallback Timezone Heuristic**: Implemented coordinate bounding box check for Japan. If reverse geocoding fails, coordinates in Japan automatically default to `"Asia/Tokyo"`, and others default to `"UTC"`.
- **Robust ISO Datetime Parsing**: Created a custom parser supporting naive datetimes, timezone offsets, and trailing `Z` characters (ensuring compatibility across Python versions).

### Changed
- **Python 3.9 Compatibility**: Replaced PEP 604 union type hints (`| None`) with `typing.Optional` to ensure compatibility with Python 3.9+.
- **Clean Constants**: Extracted magic solar altitude angles and photography cloud/rain thresholds into explicit module-level constants.
- **Code Refactoring**: Extracted the inline geocoding result sorting logic into a separate `_location_sort_key` helper function.
- **Documentation**: Updated `docs/task.md`, `docs/walkthrough.md`, and `README.md` to reflect the newly integrated subcommands and refactored logic.

### Fixed
- **Solar Key Inconsistencies**: Fixed output keys in `suncalc.py` to consistently use `_rise` and `_set` suffixes when calculations return `None` (avoiding downstream dictionary lookup crashes).

---

## [0.1.0] - 2026-05-31

### Added
- **JMA Weather Integrations**: Core weather client querying Open-Meteo with JMA MSM/GSM East-Asia optimized forecast data.
- **SQLite Local Cache**: OS-native caching of geocoded search items (24-hour expiry) and weather forecasts (15-minute expiry) to limit API requests.
- **Smart CJK Suffix Processing**: Automated generation of administrative suffix variations (e.g. `都`, `市`, `府`, `縣`) for CJK inputs to guarantee matching.
- **GPS Coordinate Parsing**: Support for decibel and Degrees/Minutes/Seconds (DMS) coordinates parsed and reverse-geocoded using OSM Nominatim.
- **Interactive Prompts**: Rich terminal layout with arrow-key selections and interactive question flows.
- **Mobile Stacking Layout**: Compact 38-column vertical text alignment (`--mobile`) optimized for terminals on mobile screens.
- **Purge Cache Command**: Included a `clean` subcommand to empty local cache databases.

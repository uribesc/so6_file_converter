# so6-file-converter

Convert **SO6** flight traffic files into [pandas](https://pandas.pydata.org/) DataFrames for data analysis.

## Installation

```bash
pip install so6-file-converter
```

Requires Python 3.8+ and pandas (installed automatically).

## Quick start

```python
from so6_converter import so6_to_df, so6_to_df_simple, so6_to_df_waypoints

# Raw SO6 file, one row per segment
df_raw = so6_to_df("example.so6")

# One row per flight, variables stored as lists
df_simple = so6_to_df_simple("./route1/example.so6")

# One row per waypoint, duplicates removed
df_waypoints = so6_to_df_waypoints(r"C:\Users\folder1\folder2\example.so6")
```

Paths can be strings or `pathlib.Path` objects.

All three functions convert coordinates from minutes to decimal degrees and add a
`country_flow` column built from the ICAO prefixes of origin and destination (e.g. `EG_LE`).

## Functions

### `so6_to_df`

Reads a **raw SO6 file** without altering its structure: one row per segment, so each
row contains two waypoints (start and end of the segment).

Columns: `segment_id`, `origin`, `destination`, `ac_type`, `time_ini_seg`, `time_end_seg`,
`fl_ini`, `fl_end`, `status`, `callsign`, `date_ini`, `date_end`, `lat_ini`, `lon_ini`,
`lat_end`, `lon_end`, `flightid`, `sequence`, `segment_length`, `segment_color`,
`flown_distance` (total distance of the flight), `country_flow`.

Typical uses: initial inspection of SO6 data, custom pipelines built on raw inputs.

### `so6_to_df_simple`

Groups records **by flight**. Each row is a flight, and `lat`, `long`, `alt`, `time` and
`date` are lists with the evolution of each variable along the route.

Columns: `callsign`, `flightid`, `origin`, `destination`, `lat`, `long`, `alt`, `time`,
`date`, `total_distance`, `ac_type`, `country_flow`.

Typical uses: flight-level trajectory analysis.

### `so6_to_df_waypoints`

Splits each segment into its two **waypoints**, one per row, and removes duplicates.

Columns: `waypoint`, `callsign`, `flightid`, `origin`, `destination`, `lat`, `lon`, `alt`,
`time`, `date`, `country_flow`.

Typical uses: route reconstruction, airspace and network analysis, flight path visualization.

## Development

```bash
pip install -e ".[test]"
pytest
```

## License

MIT

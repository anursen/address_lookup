# NJ Address Geocoding Tool

This Python script provides functionality to validate and geocode New Jersey addresses using the NJ_Geocode REST API service provided by the state of New Jersey.

## Features

- Geocode single NJ addresses with detailed match information
- Generate random NJ addresses and save them to CSV
- Test API rate limits with random NJ addresses
- Detailed logging of geocoding results and rate limit testing
- Handles multiple address match candidates with scoring

## Prerequisites

- Python 3.x
- `requests` library
- `pyproj` library (optional, for coordinate conversion)

## Installation

1. Create a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Unix/macOS
```

2. Install required packages:

```bash
pip install requests

# Optional: for coordinate conversion
pip install pyproj
```

## Usage

### Geocoding a Single Address

```python
from address_lookup import geocode_address

result = geocode_address("123 Main St, Newark, NJ")
if result:
    print(f"Matched Address: {result['matched_address']}")
    print(f"Latitude: {result['latitude']}")  # Returns in NJ State Plane coordinates
    print(f"Longitude: {result['longitude']}")  # Returns in NJ State Plane coordinates
```

### Coordinate System Information

The API returns coordinates in the **New Jersey State Plane** coordinate system (EPSG:3424/NAD83), not in standard WGS84 latitude/longitude. The `address_lookup` module provides a helper called `convert_coordinates` that performs this conversion using `pyproj`:

```python
from address_lookup import geocode_address, convert_coordinates

# Example usage:
address = "3 Sue Court, Denville, NJ"
result = geocode_address(address)

if result:
    # Get the State Plane coordinates from the API response
    state_plane_x = result['longitude']  # Around 486259.02
    state_plane_y = result['latitude']   # Around 738876.23

    # Convert to WGS84 lat/lon
    lat, lon = convert_coordinates(state_plane_x, state_plane_y)
    print(f"Address: {result['matched_address']}")
    print(f"WGS84 Coordinates: {lat:.6f}, {lon:.6f}")
    # Will print something like: 40.888888, -74.484848
```

For reference, valid WGS84 coordinates for New Jersey should be:

- Latitude: Between 38.9° and 41.4° North
- Longitude: Between -75.6° and -73.9° West

You can verify the converted coordinates by pasting them into Google Maps or OpenStreetMap.

### Generating Random Addresses

To generate random NJ addresses and save them to a CSV file:

```bash
python address_lookup.py generate [num_addresses] [output_file]
```

For example:

```bash
python address_lookup.py generate 100 my_addresses.csv
```

This will generate 100 random NJ addresses and save them to `my_addresses.csv`. If no arguments are provided, it will generate 100 addresses and save them to `generated_addresses.csv`.

### Testing Rate Limits

To test the API rate limits, run:

```bash
python address_lookup.py
```

This will:

- Generate random NJ addresses
- Make API requests with a 0.5-second delay between each
- Log all results to `rate_limit_test.txt`
- Continue until a rate limit or error is encountered
- Display summary statistics when complete

## Output

The rate limit test creates a log file (`rate_limit_test.txt`) containing:

- Timestamp for each request
- Input address
- Best match details
- All candidate matches with scores
- Coordinates for each match
- Any errors encountered

## Error Handling

The script includes robust error handling for:

- API request failures
- Rate limiting
- Invalid addresses
- Network issues

## API Information

Uses the NJ_Geocode REST API service:
`https://geo.nj.gov/arcgis/rest/services/Tasks/NJ_Geocode/GeocodeServer/findAddressCandidates`

Note: This is a public API service provided by the state of New Jersey. Please use responsibly and be mindful of rate limits.

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

The API returns coordinates in the **New Jersey State Plane** coordinate system (EPSG:3424/NAD83), not in the standard WGS84 latitude/longitude format. If you need standard GPS coordinates, you can use the following conversion function:

```python
from pyproj import Transformer

# Create a transformer object (do this once, outside your functions)
transformer = Transformer.from_crs(
    "epsg:3424",  # NJ State Plane
    "epsg:4326",  # WGS84 (standard lat/long)
    always_xy=True  # Ensure we get longitude, latitude order
)

def convert_coordinates(state_plane_x: float, state_plane_y: float) -> tuple[float, float]:
    """
    Convert NJ State Plane coordinates to WGS84 latitude/longitude.

    Args:
        state_plane_x: X coordinate in NJ State Plane
        state_plane_y: Y coordinate in NJ State Plane

    Returns:
        tuple: (latitude, longitude) in WGS84
    """
    lon, lat = transformer.transform(state_plane_x, state_plane_y)
    return lat, lon

# Example usage:
# state_plane_coords = result['longitude'], result['latitude']  # Note: x=longitude, y=latitude
# lat, lon = convert_coordinates(*state_plane_coords)
# print(f"GPS Coordinates: {lat}, {lon}")  # Will be approximately 40.89, -74.48 for central NJ
```

For New Jersey, the converted WGS84 coordinates should typically be:

- Latitude: Between 38.9° and 41.4° North
- Longitude: Between -75.6° and -73.9° West

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

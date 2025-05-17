# NJ Address Geocoding Tool

This Python script provides functionality to validate and geocode New Jersey addresses using the NJ_Geocode REST API service provided by the state of New Jersey.

## Features

- Geocode single NJ addresses with detailed match information
- Test API rate limits with random NJ addresses
- Detailed logging of geocoding results and rate limit testing
- Handles multiple address match candidates with scoring

## Prerequisites

- Python 3.x
- `requests` library

## Installation

1. Create a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Unix/macOS
```

2. Install required packages:

```bash
pip install requests
```

## Usage

### Geocoding a Single Address

```python
from address_lookup import geocode_address

result = geocode_address("123 Main St, Newark, NJ")
if result:
    print(f"Matched Address: {result['matched_address']}")
    print(f"Latitude: {result['latitude']}")
    print(f"Longitude: {result['longitude']}")
```

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

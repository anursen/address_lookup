import requests
import time
import random
import csv
from datetime import datetime


def geocode_address(address: str) -> dict:
    """
    Query the NJ_Geocode REST API to validate and geocode a single NJ address.
    Returns a dict with:
      - 'matched_address': the standardized address
      - 'latitude': Y coordinate
      - 'longitude': X coordinate
    If no match is found, returns an empty dict.
    """
    url = "https://geo.nj.gov/arcgis/rest/services/Tasks/NJ_Geocode/GeocodeServer/findAddressCandidates"
    params = {"SingleLine": address, "f": "json", "outFields": "Match_addr,Addr_type"}
    resp = requests.get(url, params=params, timeout=10)  # Adding timeout
    resp.raise_for_status()
    data = resp.json()

    candidates = data.get("candidates", [])
    if not candidates:
        return {}

    # Get all candidates with their scores
    matches = []
    # print(data)
    for candidate in candidates:
        matches.append(
            {
                "address": candidate["address"],
                "score": candidate.get("score", 0),
                "latitude": candidate["location"]["y"],
                "longitude": candidate["location"]["x"],
                "match_type": candidate.get("attributes", {}).get(
                    "Addr_type", "Unknown"
                ),
            }
        )

    return {
        "matched_address": candidates[0]["address"],
        "latitude": candidates[0]["location"]["y"],
        "longitude": candidates[0]["location"]["x"],
        "all_matches": matches,
    }


def convert_coordinates(state_plane_x: float, state_plane_y: float) -> tuple[float, float]:
    """Convert NJ State Plane coordinates to standard latitude/longitude.

    Parameters
    ----------
    state_plane_x : float
        X coordinate returned by the API (longitude in EPSG:3424)
    state_plane_y : float
        Y coordinate returned by the API (latitude in EPSG:3424)

    Returns
    -------
    tuple[float, float]
        ``(latitude, longitude)`` in WGS84 decimal degrees.
    """
    try:
        from pyproj import Transformer
    except Exception as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "pyproj is required for coordinate conversion."
        ) from exc

    transformer = Transformer.from_crs("epsg:3424", "epsg:4326", always_xy=True)
    lon, lat = transformer.transform(state_plane_x, state_plane_y)
    return lat, lon


def test_rate_limits():
    """
    Test how many requests we can make before hitting rate limits.
    Results are saved to 'rate_limit_test.txt' in real-time.
    """
    # List of random NJ cities and street types for testing
    nj_cities = ["Newark", "Jersey City", "Paterson", "Elizabeth", "Trenton", "Camden"]
    street_types = ["St", "Ave", "Rd", "Blvd", "Ln", "Dr", "Ct", "Way"]

    request_count = 0
    start_time = datetime.now()
    log_file = "rate_limit_test.txt"

    print("Testing API rate limits with random addresses...")
    print(f"Started at: {start_time}")

    # Initialize log file
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"Rate Limit Test Started at: {start_time}\n")
        f.write("Testing with random NJ addresses\n")
        f.write("================================\n")

    try:
        while True:
            try:
                # Generate a random address
                number = str(random.randint(1, 999))
                street = random.choice(["Main", "Oak", "Maple", "Cedar", "Pine", "Elm"])
                street_type = random.choice(street_types)
                city = random.choice(nj_cities)
                test_address = f"{number} {street} {street_type}, {city}, NJ"

                # Make the request
                result = geocode_address(test_address)
                request_count += 1

                # Log success with detailed response
                log_entry = (
                    f"Request {request_count} at {datetime.now()}:\n"
                    f"  Input: {test_address}\n"
                    f"  Best Match: {result.get('matched_address', 'No match')}\n"
                    f"  Coords: ({result.get('latitude', 'N/A')}, {result.get('longitude', 'N/A')})\n"
                    f"\n  All Matches:\n"
                )

                # Add all matches with their scores
                for match in result.get("all_matches", []):
                    log_entry += (
                        f"    - {match['address']}\n"
                        f"      Score: {match['score']}\n"
                        f"      Type: {match['match_type']}\n"
                        f"      Coords: ({match['latitude']}, {match['longitude']})\n"
                    )

                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry)
                    f.write("-" * 50 + "\n")

                if request_count % 10 == 0:
                    status = f"Successfully made {request_count} requests..."
                    print(status)
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(f"{status}\n")

            except requests.exceptions.RequestException as e:
                # Log failure and raise to outer try block
                log_entry = (
                    f"Request {request_count + 1} at {datetime.now()}:\n"
                    f"  Input: {test_address}\n"
                    f"  ERROR: {str(e)}\n"
                )
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry)
                    f.write("-" * 50 + "\n")
                raise e

            time.sleep(0.5)  # Reduced delay to 0.5 seconds to test faster

    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"\nRate limit reached after {request_count} requests")
        print(f"Total time: {duration:.2f} seconds")
        print(
            f"Average rate: {request_count / (duration / 60):.2f} requests per minute"
        )
        print(f"Error message: {str(e)}")
        return request_count


def generate_addresses_to_csv(
    count: int, csv_file: str = "generated_addresses.csv"
) -> None:
    """
    Generate random NJ addresses and save them to a CSV file.

    Args:
        count: Number of addresses to generate
        csv_file: Path to the output CSV file (default: generated_addresses.csv)
    """
    # List of random NJ cities and street types for testing
    nj_cities = ["Newark", "Jersey City", "Paterson", "Elizabeth", "Trenton", "Camden"]
    street_types = ["St", "Ave", "Rd", "Blvd", "Ln", "Dr", "Ct", "Way"]
    streets = ["Main", "Oak", "Maple", "Cedar", "Pine", "Elm"]

    print(f"Generating {count} random addresses to {csv_file}...")

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(
            [
                "street_number",
                "street_name",
                "street_type",
                "city",
                "state",
                "full_address",
            ]
        )

        # Generate addresses
        for _ in range(count):
            number = str(random.randint(1, 999))
            street = random.choice(streets)
            street_type = random.choice(street_types)
            city = random.choice(nj_cities)
            full_address = f"{number} {street} {street_type}, {city}, NJ"

            # Write to CSV
            writer.writerow([number, street, street_type, city, "NJ", full_address])

    print(f"Successfully generated {count} addresses to {csv_file}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        # Get number of addresses from command line or use default
        num_addresses = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        # Get output file from command line or use default
        output_file = sys.argv[3] if len(sys.argv) > 3 else "generated_addresses.csv"
        generate_addresses_to_csv(num_addresses, output_file)
    else:
        print("Starting API rate limit test...")
        test_rate_limits()

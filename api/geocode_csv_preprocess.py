import csv
import time
import requests

INPUT_CSV = 'api/fuel_prices.csv'
OUTPUT_CSV = 'api/fuel_prices_geocoded.csv'
GEOCODE_URL = 'https://photon.komoot.io/api/'


def geocode_address(address):
    try:
        response = requests.get(GEOCODE_URL, params={"q": address}, timeout=10)
        data = response.json()
        if data["features"]:
            coords = data["features"][0]["geometry"]["coordinates"]
            return coords[1], coords[0]  # (latitude, longitude)
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
    return None, None

def process_csv():
# Track already geocoded addresses to avoid duplicates
    seen_addresses = {}

    with open(INPUT_CSV, newline='', encoding='utf-8') as infile, open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['Latitude', 'Longitude']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, row in enumerate(reader, start=1):
            address = f"{row['Address']}, {row['City']}, {row['State']}"

            if address in seen_addresses:
                lat, lon = seen_addresses[address]
            else:
                lat, lon = geocode_address(address)
                seen_addresses[address] = (lat, lon)
                time.sleep(0.3)  # be polite to the API

            row['Latitude'] = lat
            row['Longitude'] = lon
            writer.writerow(row)

            if i % 50 == 0:
                print(f"Processed {i} addresses...")

    print("Geocoding complete. Saved to", OUTPUT_CSV)

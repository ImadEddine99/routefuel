import csv
import os
import polyline
from geopy.distance import geodesic
import openrouteservice
from openrouteservice.exceptions import ApiError
from environ import Env
import requests
FUEL_CSV_PATH = 'api/fuel_prices_geocoded.csv'  # Updated to use pre-geocoded CSV
MAX_RANGE_MILES = 500
MPG = 10

# Load environment variables
env = Env()
env.read_env()
API_KEY = os.getenv('ORS_API_KEY')
ORS_GEOCODE_URL = "https://api.openrouteservice.org/geocode/search"
client = openrouteservice.Client(key=API_KEY)

def load_fuel_stops():
    stops = []
    with open(FUEL_CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                lat = float(row['Latitude'])
                lon = float(row['Longitude'])
                  
                location = (lat, lon)
                if location !=('','') and location !=(None,None):
                    # print(f" ({lat}, {lon}) ")
                    stops.append({
                    'name': row['Truckstop Name'],
                    'address': f"{row['Address']}, {row['City']}, {row['State']}",
                    'price': float(row['Retail Price']),
                    'location': location
                })
            except (ValueError, KeyError):
                continue  # skip rows with invalid coordinates
        print(len(stops))
    return stops

def get_route_data(start_coords, end_coords):
    coords = [
        geocode_location(start_coords),  # Start location
        geocode_location(end_coords)    # End location
    ]

    print(f"start_coords : {start_coords}")
    print(f"end_coords : {end_coords}")

    route = client.directions(
        coordinates=coords,
        profile="driving-car",
        format="geojson",
        radiuses=[2000, 2000]
    )

    return {
        'geojson': route['features'][0]['geometry'],
        'distance': route['features'][0]['properties']['segments'][0]['distance'] / 1609.34
    }

def geocode_location(location):
    params = {
        "api_key": API_KEY,
        "text": location,
        "size": 1
    }
    response = requests.get(ORS_GEOCODE_URL, params=params)
    response.raise_for_status()
    features = response.json()["features"]
    if not features:
        raise ValueError(f"No coordinates found for location: {location}")
    coords = features[0]["geometry"]["coordinates"]
    return coords

def find_optimal_fuel_stops(route_data):
    total_distance = route_data['distance']
    steps = int(total_distance / MAX_RANGE_MILES) + 1
    stops = []
    fuel_stops = load_fuel_stops()

    route_points = route_data['geojson']['coordinates']  # [lon, lat]

    for i in range(steps):
        idx = int(i * len(route_points) / steps)
        lon, lat = route_points[idx]
        current_location = (lat, lon)

        nearby = sorted([
            s for s in fuel_stops
            if s.get('location') and geodesic(current_location, s['location']).miles < 25
        ], key=lambda s: s['price'])

        print(f"[Step {i}] Location: {current_location}, Nearby found: {len(nearby)}")

        if nearby:
            stops.append(nearby[0])

    return stops


def calculate_total_cost(route_data, stops):
    total_distance = route_data['distance']
    total_gallons = total_distance / MPG

    if not stops:
        return 0  # or raise Exception("No fuel stops found")

    gallons_per_stop = total_gallons / len(stops)
    return sum(s['price'] * gallons_per_stop for s in stops)

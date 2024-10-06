import requests
import json
from datetime import datetime, timedelta
from shapely.geometry import shape, box  # For geometric operations
from shapely.validation import explain_validity

def get_landslide_nowcast_data():
    """
    Fetch the global landslide nowcast data from NASA's PMM Publisher API for the specified date.
    """
    one_week_ago = datetime.now() - timedelta(weeks=1)
    date_str = one_week_ago.strftime('%Y%m%d')  # Format: YYYYMMDD

    url = f"https://pmmpublisher.pps.eosdis.nasa.gov/opensearch?q=global_landslide_nowcast&lat=38&lon=100&limit=1&startTime={date_str}&endTime={date_str}"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code} - {response.text}")
        return None

def download_geojson(geojson_url, filename):
    """
    Download the GeoJSON file from the provided URL and save it locally.
    """
    try:
        geojson_response = requests.get(geojson_url)
        if geojson_response.status_code == 200:
            with open(filename, 'w') as file:
                json.dump(geojson_response.json(), file, indent=4)
            print(f"GeoJSON file downloaded and saved as: {filename}")
        else:
            print(f"Error downloading GeoJSON: {geojson_response.status_code} - {geojson_response.text}")
    except Exception as e:
        print(f"An error occurred while downloading the GeoJSON: {e}")

def validate_geojson_geometry(geojson_file):
    """
    Validate all geometries in the GeoJSON file and return whether they are valid.
    """
    with open(geojson_file) as f:
        geojson_data = json.load(f)

    for feature in geojson_data['features']:
        geom = shape(feature['geometry'])
        if not geom.is_valid:
            print(f"Invalid geometry found: {explain_validity(geom)}")
            return False  # If any geometry is invalid, return False
    return True  # All geometries are valid

def crop_geojson_to_south_india(geojson_file):
    """
    Crop the GeoJSON data to South India.
    """
    south_india_bbox = box(77.0, 8.0, 92.0, 37.0)  # Bounding box for South India

    with open(geojson_file) as f:
        geojson_data = json.load(f)

    cropped_features = []
    for feature in geojson_data['features']:
        geom = shape(feature['geometry'])
        if south_india_bbox.intersects(geom):
            cropped_features.append(feature)

    cropped_geojson = {
        "type": "FeatureCollection",
        "features": cropped_features
    }

    return cropped_geojson

def fetch_and_process_data(retries=3):
    """
    Fetch and process landslide data with retries if invalid geometry is encountered.
    """
    attempt = 0
    while attempt < retries:
        attempt += 1
        print(f"Attempt {attempt} to fetch and process data")

        # Step 1: Fetch the landslide nowcast data
        landslide_data = get_landslide_nowcast_data()

        if not landslide_data:
            print(f"Failed to fetch landslide data on attempt {attempt}. Retrying...")
            continue

        save_json_to_file(landslide_data, "landslide_nowcast_data.json")

        # Step 2: Extract the GeoJSON URL
        geojson_url = None
        for item in landslide_data.get("items", []):
            for action in item.get("action", []):
                if action.get("@type") == "ojo:export":
                    for export in action.get("using", []):
                        if export.get("mediaType") == "application/json":
                            geojson_url = export["url"]
                            break
                if geojson_url:
                    break
            if geojson_url:
                break

        if not geojson_url:
            print("GeoJSON URL not found. Retrying...")
            continue

        # Step 3: Download the GeoJSON file
        download_geojson(geojson_url, "landslide_nowcast.geojson")

        # Step 4: Validate the GeoJSON file
        if not validate_geojson_geometry("landslide_nowcast.geojson"):
            print(f"Invalid geometry found on attempt {attempt}. Retrying...")
            continue  # Retry by fetching the data again

        # Step 5: Crop the GeoJSON to South India and save
        cropped_geojson = crop_geojson_to_south_india("landslide_nowcast.geojson")
        save_json_to_file(cropped_geojson, "cropped_landslide_nowcast.geojson")

        print("Data processed successfully.")
        return  # Exit the function after successful completion

    print("All attempts failed due to invalid geometries or other errors.")

def save_json_to_file(json_data, filename):
    """
    Save the JSON data to a file.
    """
    try:
        with open(filename, 'w') as file:
            json.dump(json_data, file, indent=4)
        print(f"JSON data saved to file: {filename}")
    except Exception as e:
        print(f"An error occurred while saving JSON data to file: {e}")

if __name__ == "__main__":
    fetch_and_process_data()


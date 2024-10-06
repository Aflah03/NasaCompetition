import requests
import json
from datetime import datetime, timedelta
from shapely.geometry import shape, box  # For geometric operations

def get_landslide_nowcast_data():
    """
    Fetch the global landslide nowcast data from NASA's PMM Publisher API for the specified date.
    """
    # Calculate the date for one week ago
    one_week_ago = datetime.now() - timedelta(weeks=1)
    date_str = one_week_ago.strftime('%Y%m%d')  # Format: YYYYMMDD

    # Define the request URL
    url = f"https://pmmpublisher.pps.eosdis.nasa.gov/opensearch?q=global_landslide_nowcast&lat=38&lon=100&limit=1&startTime={date_str}&endTime={date_str}"

    # Make the request to the API
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the JSON response
        json_data = response.json()
        return json_data
    else:
        print(f"Error fetching data: {response.status_code} - {response.text}")
        return None

def download_geojson(geojson_url, filename):
    """
    Download the GeoJSON file from the provided URL and save it locally.
    """
    try:
        # Make the GET request to download the GeoJSON
        geojson_response = requests.get(geojson_url)

        if geojson_response.status_code == 200:
            # Write the content to a file
            with open(filename, 'w') as file:
                json.dump(geojson_response.json(), file, indent=4)
            print(f"GeoJSON file downloaded and saved as: {filename}")
        else:
            print(f"Error downloading GeoJSON: {geojson_response.status_code} - {geojson_response.text}")

    except Exception as e:
        print(f"An error occurred while downloading the GeoJSON: {e}")

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

def crop_geojson_to_south_india(geojson_file):
    """
    Crop the GeoJSON data to South India.
    """
    south_india_bbox = box(77.0, 8.0, 92.0, 37.0)  # Bounding box for South India

    with open(geojson_file) as f:
        geojson_data = json.load(f)

    # Prepare a new GeoJSON structure for cropped data
    cropped_features = []

    for feature in geojson_data['features']:
        geom = shape(feature['geometry'])
        if south_india_bbox.intersects(geom):  # Check if the feature intersects with the bounding box
            cropped_features.append(feature)

    cropped_geojson = {
        "type": "FeatureCollection",
        "features": cropped_features
    }

    return cropped_geojson

def fetch_and_process_data(retries=3):
    """
    Fetch and process landslide data.
    """
    for attempt in range(retries):
        # Get the landslide nowcast data
        landslide_data = get_landslide_nowcast_data()

        # If we got valid data, break the loop
        if landslide_data:
            save_json_to_file(landslide_data, "landslide_nowcast_data.json")  # Save the JSON data to a file

            # Find the GeoJSON URL from the "export" actions
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

            # Download the GeoJSON if the URL was found
            if geojson_url:
                download_geojson(geojson_url, "landslide_nowcast.geojson")

                # Crop the GeoJSON to South India
                cropped_geojson = crop_geojson_to_south_india("landslide_nowcast.geojson")

                # Save the cropped GeoJSON to a file (optional)
                save_json_to_file(cropped_geojson, "cropped_landslide_nowcast.geojson")
                return  # Exit the function after successful completion
            else:
                print("GeoJSON URL not found in the response.")
                return
        else:
            print(f"Attempt {attempt + 1} failed. Retrying...")

    print("All attempts failed. Please check the network or the API.")

if __name__ == "__main__":
    fetch_and_process_data()


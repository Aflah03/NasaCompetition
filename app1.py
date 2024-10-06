from flask import Flask, render_template, request, jsonify
import os
import json
import threading
import time
from getc import fetch_and_process_data  # Import the function from gety.py
from shapely.geometry import shape, Point
from twilio.rest import Client  # Import Twilio Client

app = Flask(__name__)

# Twilio credentials
TWILIO_ACCOUNT_SID = 'AC9ad2e93b844170b4a4623490d726e9e2'  # Replace with your Twilio Account SID
TWILIO_AUTH_TOKEN = '771d28c59f9704f40aa4778d6a43b202'      # Replace with your Twilio Auth Token
TWILIO_PHONE_NUMBER = '+14782161002'  # Replace with your Twilio phone number

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Global variable to track the last fetch time
last_fetch_time = 0
fetch_interval = 10800  # 3 hours in seconds

# Global list to store user information
user_data = []
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import threading
import time
from getc import fetch_and_process_data
from shapely.geometry import shape, Point
from twilio.rest import Client

app = Flask(__name__)

# Twilio credentials and other variables/functions remain unchanged

# Main index route
@app.route('/')
def index():
    return render_template('index.html')

# Route for the community page
@app.route('/community')
def community():
    return render_template('community.html')

# Route for the finance page
@app.route('/finance')
def finance():
    return render_template('finance.html')

# Route for the suraksha/alert page
@app.route('/alert')
def alert():
    return render_template('alert.html')

# Route for the house/user information page
@app.route('/house')
@app.route('/user_info')
def house():
    return render_template('user_info.html')

# Route for the insurance page
@app.route('/insurance')
def insurance():
    return render_template('insurance.html')

@app.route('/health-insurance')
def health_insurance():
    return render_template('health-insurance.html')

@app.route('/house-form')
def house_form():
    return render_template('house-form.html')

@app.route('/house-insurance')
def house_insurance():
    return render_template('house-insurance.html')

@app.route('/job-form')
def job_form():
    return render_template('job-form.html')

@app.route('/life-form')
def life_form():
    return render_template('life-form')

@app.route('/life-insurance')
def life_insurance():
    return render_template('life-insurance.html')

@app.route('/job-insurance')
def job_insurance():
    return render_template('job-insurance.html')

# Route for the swapnam page
@app.route('/swapnam')
def swapnam():
    return render_template('swapnam.html')

# Rest of your existing code (user_info route, Twilio logic, etc.)

def call_user(phone_number):
    """Call the user using Twilio."""
    try:
        call = twilio_client.calls.create(
            to=phone_number,
            from_= '+14782161002',
            twiml='<Response><Say>Your location is in a danger zone. Please take necessary precautions!</Say></Response>'
        )
        print(f"Calling {phone_number}... (Twilio Call SID: {call.sid})")
    except Exception as e:
        print(f"Failed to call {phone_number}: {e}")

def is_user_in_danger_zone(lat, lon, geojson_data):
    """Check if the user's location falls in a danger zone."""
    point = Point(lon, lat)
    
    # Iterate through all features in the GeoJSON data
    for feature in geojson_data['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            return True
    return False

def check_users_in_danger_zones(users=None):
    """Check all users' locations against the danger zones."""
    if users is None:
        users = user_data  # Default to all users if none provided
    
    if not users:
        print("No users to check yet.")
        return
    
    try:
        with open('cropped_landslide_nowcast.geojson') as f:
            geojson_data = json.load(f)
    except Exception as e:
        print(f"Error loading GeoJSON data: {e}")
        return

    # Iterate over each user in the list and check danger zones
    for user in users:
        phone = user['phone']
        latitude = float(user['latitude'])
        longitude = float(user['longitude'])

        # Check if the user's location is in a danger zone
        if is_user_in_danger_zone(latitude, longitude, geojson_data):
            call_user(phone)  # Call the user
        else:
            print(f"User {phone} is in a safe zone.")

# Background thread to check danger zones every 3 hours
def periodic_check():
    global last_fetch_time
    while True:
        current_time = time.time()

        # Check if it's time to fetch new data
        if current_time - last_fetch_time >= fetch_interval:
            fetch_and_process_data()  # Fetch and process the latest data
            last_fetch_time = current_time  # Update the last fetch time

            print("Running danger zone check after fetching new data...")
            check_users_in_danger_zones()  # Check all users after fetching new data

        # Check for users in danger zones every 3 hours (as part of the same loop)
        check_users_in_danger_zones()  # Check all users
        time.sleep(10800)  # Wait for 3 hours



@app.route('/geojson')
def geojson():
    try:
        with open('cropped_landslide_nowcast.geojson') as f:  # Use the cropped GeoJSON file
            data = json.load(f)
            return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/user_info', methods=['GET', 'POST'])
def user_info():
    if request.method == 'POST':
        phone = request.form['phone']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        
        # Append user data to the global list
        user_data.append({
            'phone': phone,
            'latitude': latitude,
            'longitude': longitude
        })
        print(f'User data: {user_data}')

        # Immediately check if the newly added user is in a danger zone
        check_users_in_danger_zones([user_data[-1]])  # Check only the newly added user
        
        return f'Thank you! Phone Number: {phone}, Location: ({latitude}, {longitude})'
    return render_template('user_info.html')

@app.route('/show_users')
def show_users():
    return jsonify(user_data)

if __name__ == "__main__":
    # Start the background thread to check danger zones every 3 hours
    port= int(os.environ.get("PORT",5000))
    check_thread = threading.Thread(target=periodic_check)
    check_thread.daemon = True  # Daemon thread exits when the main program exits
    check_thread.start()
    
    app.run(debug=True, host='0.0.0.0',port=port)

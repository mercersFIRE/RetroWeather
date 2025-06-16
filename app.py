from flask import Flask, request, jsonify, render_template
import requests
import json
import os

app = Flask(__name__)

API_KEY = "46c1fb2ea6f9fd4b22b521dd4c05983a"

# Load saved locations (can store max 5)
SAVED_LOCATIONS_FILE = 'saved_locations.json'

if not os.path.exists(SAVED_LOCATIONS_FILE):
    with open(SAVED_LOCATIONS_FILE, 'w') as f:
        json.dump([], f)

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    else:
        return {"error": "City not found or API error"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather')
def weather():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City not provided"}), 400
    data = get_weather(city)
    return jsonify(data)

@app.route('/locations', methods=['GET', 'POST'])
def manage_locations():
    with open(SAVED_LOCATIONS_FILE, 'r') as f:
        locations = json.load(f)

    if request.method == 'POST':
        new_city = request.json.get('city')
        if new_city and new_city not in locations:
            if len(locations) >= 5:
                return jsonify({"error": "Maximum 5 locations allowed"}), 400
            locations.append(new_city)
            with open(SAVED_LOCATIONS_FILE, 'w') as f:
                json.dump(locations, f)
    return jsonify(locations)

@app.route('/alert')
def weather_alert():
    city = request.args.get('city')
    data = get_weather(city)
    if 'wind' in data and data['wind']['speed'] > 10:
        return jsonify({"alert": "High wind speed detected!"})
    return jsonify({"alert": "Weather is normal."})

@app.route('/weatherByCoords')
def weather_by_coords():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"error": "Coordinates missing"}), 400

    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    res = requests.get(url)
    return jsonify(res.json())
    
@app.route('/locations/delete', methods=['DELETE'])
def delete_location():
    city_to_delete = request.args.get('city')
    with open(SAVED_LOCATIONS_FILE, 'r') as f:
        locations = json.load(f)

    if city_to_delete in locations:
        locations.remove(city_to_delete)
        with open(SAVED_LOCATIONS_FILE, 'w') as f:
            json.dump(locations, f)

    return jsonify(locations)

if __name__ == '__main__':
    app.run(debug=True)

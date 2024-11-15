import requests
from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Replace with your actual Google API key
API_KEY = "AIzaSyBX0EF6pxR9tMfYPaHTHHTy-vhwdjZ1rIo"

# Function to connect to the SQLite database
def connect_db():
    conn = sqlite3.connect('project.db')
    return conn

# Function to create the database and tables if they don't exist
def create_database():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Create the search_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT,
            category TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create the click_history table to track "Get Directions" clicks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS click_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database and tables created successfully.")

# Function to categorize a place based on keywords in its name
def categorize_place(name):
    name = name.lower()
    if "temple" in name or "mandir" in name:
        return "Temple"
    elif "waterfall" in name or "lake" in name or "dam" in name:
        return "Natural Attraction"
    elif "museum" in name or "gallery" in name:
        return "Museum"
    elif "fort" in name or "palace" in name or "heritage" in name:
        return "Historical Place"
    elif "farm" in name or "agro" in name:
        return "Agricultural"
    elif "hiking" in name or "trail" in name or "trek" in name:
        return "Hiking"
    else:
        return "Others"

# Function to get coordinates of a location
def get_coordinates(location):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={API_KEY}"
    response = requests.get(geocode_url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            location_data = data['results'][0]['geometry']['location']
            return location_data['lat'], location_data['lng']
    return None, None

# Function to get tourist spots using latitude and longitude
def get_tourist_spots(lat, lng):
    places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=5000&type=tourist_attraction&key={API_KEY}"
    response = requests.get(places_url)
    if response.status_code == 200:
        data = response.json()
        spots = []
        for place in data['results']:
            photo_reference = place['photos'][0]['photo_reference'] if 'photos' in place else None
            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={API_KEY}" if photo_reference else None
            category = categorize_place(place.get('name', ''))

            spots.append({
                'name': place.get('name'),
                'address': place.get('vicinity'),
                'rating': place.get('rating', 'No rating available'),
                'category': category,
                'place_id': place.get('place_id'),
                'photo_url': photo_url,
                'latitude': place['geometry']['location']['lat'],
                'longitude': place['geometry']['location']['lng']
            })
        return spots
    return []

# Route to handle search and store in the database
@app.route('/search', methods=['POST'])
def search():
    data = request.json
    location = data.get('location')
    lat, lng = get_coordinates(location)
    
    if lat and lng:
        spots = get_tourist_spots(lat, lng)
        
        # Store the search data in the database only once per request
        if spots:
            conn = connect_db()
            cursor = conn.cursor()
            # Store the search location and category once per search request
            cursor.execute(
                'INSERT INTO search_history (location, category, timestamp) VALUES (?, ?, ?)',
                (location, spots[0]['category'], datetime.now())
            )
            conn.commit()
            conn.close()
        
        return jsonify(spots)
    else:
        return jsonify({"error": "Location not found"}), 404

# Route to record clicks on the "Get Directions" button
@app.route('/click', methods=['POST'])
def record_click():
    data = request.json
    category = data.get('category')  # Category of the place for which directions are requested

    # Ensure the category is provided
    if not category:
        return jsonify({"error": "Category is required"}), 400

    # Insert the clicked category into the click_history table
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO click_history (category, timestamp) VALUES (?, ?)',
        (category, datetime.now())
    )
    conn.commit()
    conn.close()

    # Respond with a success message
    return jsonify({"message": "Click recorded successfully."})

# Function to get the most frequently clicked category
def get_most_clicked_category():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Query to find the most frequently clicked category
    cursor.execute(
        'SELECT category, COUNT(category) as frequency FROM click_history GROUP BY category ORDER BY frequency DESC LIMIT 1'
    )
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

# Route to provide recommendations based on most clicked category
@app.route('/recommend', methods=['GET'])
def recommend():
    # Get the user's most frequently clicked category
    favorite_category = get_most_clicked_category()
    
    if favorite_category:
        # Fetch places from Google Places API based on the favorite category
        lat, lng = 18.6298, 73.7997  # Example coordinates (PCU)
        places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=5000&type=tourist_attraction&keyword={favorite_category}&key={API_KEY}"
        
        response = requests.get(places_url)
        if response.status_code == 200:
            data = response.json()
            recommendations = []
            for place in data['results']:
                recommendations.append({
                    'name': place.get('name'),
                    'address': place.get('vicinity'),
                    'rating': place.get('rating', 'No rating available')
                })
            return jsonify(recommendations)
    
    return jsonify({"message": "No recommendations available."}), 404

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Initialize the database when the app starts
create_database()

if __name__ == '__main__':
    app.run(debug=True)

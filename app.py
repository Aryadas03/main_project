from flask import Flask, render_template, request, jsonify
import requests
import joblib
import numpy as np
import os

app = Flask(__name__)

# WAQI API configuration
# IMPORTANT: Replace this with your actual token from https://aqicn.org/data-platform/token/
WAQI_TOKEN = "00bd16f610bc271e71de5aa0e959a814d4b08b2c"

# Load the trained model and scaler
MODEL_PATH = 'best_aqi_model.pkl'
SCALER_PATH = 'scaler.pkl'

# Initialize model and scaler
model = None
scaler = None

try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"✅ Model loaded successfully from {MODEL_PATH}")
    else:
        print(f"⚠️  Model file not found: {MODEL_PATH}")
        
    if os.path.exists(SCALER_PATH):
        scaler = joblib.load(SCALER_PATH)
        print(f"✅ Scaler loaded successfully from {SCALER_PATH}")
    else:
        print(f"⚠️  Scaler file not found: {SCALER_PATH}")
except Exception as e:
    print(f"❌ Error loading model/scaler: {e}")

def get_aqi_category(aqi_value):
    """Determine AQI category based on value"""
    if aqi_value <= 50:
        return "Good", "#00E400"
    elif aqi_value <= 100:
        return "Moderate", "#FFFF00"
    elif aqi_value <= 150:
        return "Unhealthy for Sensitive Groups", "#FF7E00"
    elif aqi_value <= 200:
        return "Unhealthy", "#FF0000"
    elif aqi_value <= 300:
        return "Very Unhealthy", "#8F3F97"
    else:
        return "Hazardous", "#7E0023"

def fetch_air_quality_data(location):
    """Fetch air quality data from WAQI API"""
    try:
        # Get data from WAQI API
        url = f"https://api.waqi.info/feed/{location}/?token={WAQI_TOKEN}"
        print(f"Fetching data from: {url}")
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data['status'] != 'ok':
            error_msg = data.get('data', 'Location not found or API error')
            print(f"API Error: {error_msg}")
            return None, f"Error: {error_msg}"
        
        # Extract pollutant data
        iaqi = data['data'].get('iaqi', {})
        
        # Extract values, default to 0 if not available
        pollutants = {
            'pm25': iaqi.get('pm25', {}).get('v', 0) or 0,
            'pm10': iaqi.get('pm10', {}).get('v', 0) or 0,
            'no': iaqi.get('no', {}).get('v', 0) or 0,
            'no2': iaqi.get('no2', {}).get('v', 0) or 0,
            'nox': iaqi.get('nox', {}).get('v', 0) or 0,
            'nh3': iaqi.get('nh3', {}).get('v', 0) or 0,
            'co': iaqi.get('co', {}).get('v', 0) or 0,
            'so2': iaqi.get('so2', {}).get('v', 0) or 0,
            'o3': iaqi.get('o3', {}).get('v', 0) or 0,
            'benzene': iaqi.get('benzene', {}).get('v', 0) or 0,
            'toluene': iaqi.get('toluene', {}).get('v', 0) or 0,
            'xylene': iaqi.get('xylene', {}).get('v', 0) or 0
        }
        
        # Get current AQI from API
        current_aqi = data['data'].get('aqi', None)
        city_name = data['data']['city']['name']
        
        print(f"✅ Data fetched successfully for {city_name}")
        
        return {
            'pollutants': pollutants,
            'current_aqi': current_aqi,
            'city': city_name
        }, None
        
    except requests.exceptions.Timeout:
        return None, "Request timeout. Please try again."
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {str(e)}"
    except Exception as e:
        return None, f"Error fetching data: {str(e)}"

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/get_air_quality', methods=['POST'])
def get_air_quality():
    """Fetch air quality data for a location"""
    try:
        location = request.json.get('location', '').strip()
        
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        
        # Fetch data from WAQI
        result, error = fetch_air_quality_data(location)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in get_air_quality: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict_aqi', methods=['POST'])
def predict_aqi():
    """Predict AQI using the trained model"""
    try:
        # Check if model and scaler are loaded
        if model is None or scaler is None:
            return jsonify({
                'error': 'Model not loaded. Please ensure best_aqi_model.pkl and scaler.pkl are in the project folder.'
            }), 500
        
        # Get pollutant values from request
        data = request.json
        pollutants = data.get('pollutants', {})
        
        # Prepare features in the correct order (matching training data)
        features = [
            float(pollutants.get('pm25', 0) or 0),
            float(pollutants.get('pm10', 0) or 0),
            float(pollutants.get('no', 0) or 0),
            float(pollutants.get('no2', 0) or 0),
            float(pollutants.get('nox', 0) or 0),
            float(pollutants.get('nh3', 0) or 0),
            float(pollutants.get('co', 0) or 0),
            float(pollutants.get('so2', 0) or 0),
            float(pollutants.get('o3', 0) or 0),
            float(pollutants.get('benzene', 0) or 0),
            float(pollutants.get('toluene', 0) or 0),
            float(pollutants.get('xylene', 0) or 0)
        ]
        
        print(f"Features: {features}")
        
        # Scale features
        features_scaled = scaler.transform([features])
        
        # Make prediction
        predicted_aqi = model.predict(features_scaled)[0]
        predicted_aqi = float(predicted_aqi)
        
        print(f"Predicted AQI: {predicted_aqi}")
        
        # Get category
        category, color = get_aqi_category(predicted_aqi)
        
        return jsonify({
            'predicted_aqi': round(predicted_aqi, 2),
            'category': category,
            'color': color
        })
        
    except Exception as e:
        print(f"Error in predict_aqi: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'scaler_loaded': scaler is not None,
        'api_configured': WAQI_TOKEN != "YOUR_TOKEN_HERE"
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🌍 AQI Predictor - Starting Application")
    print("=" * 60)
    print(f"Model loaded: {'✅ Yes' if model else '❌ No'}")
    print(f"Scaler loaded: {'✅ Yes' if scaler else '❌ No'}")
    print(f"API token configured: {'✅ Yes' if WAQI_TOKEN != 'YOUR_TOKEN_HERE' else '❌ No'}")
    print("=" * 60)
    print()
    print("🚀 Starting Flask server...")
    print("📍 Open your browser and visit: http://localhost:5000")
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
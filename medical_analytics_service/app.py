from flask import Flask, jsonify, request, send_from_directory
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static')

# Get API configuration from environment variables
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5001/api')
API_TOKEN = os.getenv('API_TOKEN')

print("DEBUG: API Configuration:")
print(f"DEBUG: API_BASE_URL: {API_BASE_URL}")
print(f"DEBUG: API_TOKEN present: {'Yes' if API_TOKEN else 'No'}")

# Initialize API headers with token
API_HEADERS = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

print("DEBUG: API Headers:", API_HEADERS)

def fetch_data(endpoint):
    """Fetch data from the main API with error handling"""
    try:
        print(f"DEBUG: Fetching from {API_BASE_URL}/{endpoint}")
        print(f"DEBUG: Using headers: {API_HEADERS}")
        
        response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=API_HEADERS)
        print(f"DEBUG: Response status: {response.status_code}")
        print(f"DEBUG: Response content: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"DEBUG: Parsed JSON data: {data}")
                return data
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON decode error: {str(e)}")
                return {"error": f"Failed to decode response: {str(e)}"}
        else:
            print(f"DEBUG: Error response: {response.text}")
            return {"error": f"API returned status {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Request error: {str(e)}")
        return {"error": f"Failed to fetch data: {str(e)}"}
    except Exception as e:
        print(f"DEBUG: Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

@app.route('/')
def dashboard():
    """Serve the dashboard page"""
    return send_from_directory('static', 'dashboard.html')

@app.route('/analytics/patient-stats')
def get_patient_stats():
    """Get patient statistics"""
    try:
        data = fetch_data('patients')
        if "error" in data:
            app.logger.error(f"Error in patient stats: {data['error']}")
            return jsonify({"error": data["error"]}), 500
            
        # Process patient data
        total_patients = len(data)
        ages = [patient.get('age', 0) for patient in data if patient.get('age') is not None]
        avg_age = sum(ages) / len(ages) if ages else 0
        
        # Calculate age distribution
        age_ranges = {
            '0-18': 0,
            '19-30': 0,
            '31-50': 0,
            '51-70': 0,
            '70+': 0
        }
        
        for age in ages:
            if age <= 18:
                age_ranges['0-18'] += 1
            elif age <= 30:
                age_ranges['19-30'] += 1
            elif age <= 50:
                age_ranges['31-50'] += 1
            elif age <= 70:
                age_ranges['51-70'] += 1
            else:
                age_ranges['70+'] += 1
        
        return jsonify({
            'total_patients': total_patients,
            'average_age': round(avg_age, 2),
            'age_distribution': age_ranges
        })
    except Exception as e:
        app.logger.error(f"Unexpected error in patient stats: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/analytics/visit-trends')
def get_visit_trends():
    """Get visit trends"""
    try:
        days = request.args.get('days', default=30, type=int)
        if days <= 0:
            return jsonify({
                "error": "Days parameter must be a positive number",
                "status": "error"
            }), 400
            
        data = fetch_data('visits')
        if "error" in data:
            app.logger.error(f"Error in visit trends: {data['error']}")
            return jsonify({"error": data["error"]}), 500
            
        # Process visit data
        daily_visits = {}
        for visit in data:
            try:
                # Parse the ISO format date
                visit_date = datetime.strptime(visit['visit_date'], '%Y-%m-%dT%H:%M:%S.%f')
                date_str = visit_date.strftime('%Y-%m-%d')
                daily_visits[date_str] = daily_visits.get(date_str, 0) + 1
            except (ValueError, TypeError, KeyError) as e:
                print(f"DEBUG: Error processing visit date: {visit.get('visit_date')}, Error: {str(e)}")
                continue
        
        # Calculate total visits
        total_visits = sum(daily_visits.values())
        
        # Calculate average daily visits
        avg_daily = total_visits / days if days > 0 else 0
        
        return jsonify({
            'daily_visits': daily_visits,
            'total_visits': total_visits,
            'average_daily_visits': avg_daily,
            'period': f"Last {days} days"
        })
    except Exception as e:
        app.logger.error(f"Unexpected error in visit trends: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/analytics/prescription-analysis')
def get_prescription_analysis():
    """Get prescription analysis"""
    try:
        data = fetch_data('prescriptions')
        if "error" in data:
            app.logger.error(f"Error in prescription analysis: {data['error']}")
            return jsonify({"error": data["error"]}), 500
            
        # Process prescription data
        drug_usage = {}
        duration_analysis = {
            '1-3 days': 0,
            '4-7 days': 0,
            '8-14 days': 0,
            '15+ days': 0
        }
        
        for prescription in data:
            # Count drug usage
            drug = prescription.get('drug_name')
            if drug and isinstance(drug, str) and drug.strip():
                drug = drug.strip()  # Remove any whitespace
                drug_usage[drug] = drug_usage.get(drug, 0) + 1
            
            # Analyze duration
            duration = prescription.get('duration', '')
            if isinstance(duration, str):
                try:
                    # Extract numeric value from duration string
                    days_str = ''.join(filter(str.isdigit, duration))
                    if days_str:  # Only process if we found digits
                        days = int(days_str)
                        if days <= 3:
                            duration_analysis['1-3 days'] += 1
                        elif days <= 7:
                            duration_analysis['4-7 days'] += 1
                        elif days <= 14:
                            duration_analysis['8-14 days'] += 1
                        else:
                            duration_analysis['15+ days'] += 1
                except ValueError:
                    continue
        
        # Sort drugs by usage
        sorted_drugs = sorted(drug_usage.items(), key=lambda x: x[1], reverse=True)
        most_prescribed = dict(sorted_drugs[:5])  # Top 5 most prescribed drugs
        
        return jsonify({
            'total_prescriptions': len(data),
            'unique_drugs': len(drug_usage),
            'most_prescribed_drugs': most_prescribed,
            'duration_analysis': duration_analysis
        })
    except Exception as e:
        app.logger.error(f"Unexpected error in prescription analysis: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/analytics/doctor-workload')
def get_doctor_workload():
    """Get doctor workload analysis"""
    try:
        # Get visits data first
        visits_data = fetch_data('visits')
        if "error" in visits_data:
            app.logger.error(f"Error in doctor workload: {visits_data['error']}")
            return jsonify({"error": visits_data["error"]}), 500
            
        # Process doctor data from visits
        doctor_stats = {}
        for visit in visits_data:
            doctor_id = visit.get('doctor_id')
            if doctor_id:
                if doctor_id not in doctor_stats:
                    doctor_stats[doctor_id] = {
                        'name': f"Doctor {doctor_id}",  # Use ID as name since we don't have doctor names
                        'visits': 0,
                        'prescriptions': 0,
                        'diagnoses': set()
                    }
                doctor_stats[doctor_id]['visits'] += 1
                diagnosis = visit.get('diagnosis')
                if diagnosis:
                    doctor_stats[doctor_id]['diagnoses'].add(diagnosis)
        
        # Get prescriptions data
        prescriptions_data = fetch_data('prescriptions')
        if "error" not in prescriptions_data:
            for prescription in prescriptions_data:
                doctor_id = prescription.get('doctor_id')
                if doctor_id in doctor_stats:
                    doctor_stats[doctor_id]['prescriptions'] += 1
        
        # Convert sets to lists for JSON serialization
        for stats in doctor_stats.values():
            stats['diagnoses'] = list(stats['diagnoses'])
        
        return jsonify({
            'total_doctors': len(doctor_stats),
            'doctor_stats': doctor_stats
        })
    except Exception as e:
        app.logger.error(f"Unexpected error in doctor workload: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/test/raw-data')
def test_raw_data():
    """Test endpoint to see raw data from main API"""
    try:
        visits = fetch_data('visits')
        prescriptions = fetch_data('prescriptions')
        
        return jsonify({
            'visits': visits,
            'prescriptions': prescriptions,
            'api_config': {
                'base_url': API_BASE_URL,
                'token_present': bool(API_TOKEN),
                'headers': API_HEADERS
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug/config')
def debug_config():
    """Debug endpoint to check configuration"""
    return jsonify({
        'api_base_url': API_BASE_URL,
        'token_present': bool(API_TOKEN),
        'token_length': len(API_TOKEN) if API_TOKEN else 0,
        'headers': API_HEADERS
    })

if __name__ == '__main__':
    app.run(port=5002, debug=True) 
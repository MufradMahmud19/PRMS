# Medical Analytics Service

This auxiliary service provides statistical analysis and insights for the Patient Record Management System (PRMS).

## Features

- Patient Statistics: Age distribution and demographics
- Visit Trends: Daily visit patterns and trends
- Prescription Analysis: Drug usage patterns and durations
- Doctor Workload: Performance metrics and workload distribution

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with:
```
API_BASE_URL=http://localhost:5001/api
API_TOKEN=your_jwt_token_here
```

3. Start the service:
```bash
python app.py
```

The service will run on port 5002.

## API Endpoints

### 1. Patient Statistics
- **URL**: `/analytics/patient-stats`
- **Method**: GET
- **Response**: Total patients, average age, and age distribution

### 2. Visit Trends
- **URL**: `/analytics/visit-trends`
- **Method**: GET
- **Query Parameters**: 
  - `days` (optional): Number of days to analyze (default: 30)
- **Response**: Visit statistics for the specified period

### 3. Prescription Analysis
- **URL**: `/analytics/prescription-analysis`
- **Method**: GET
- **Response**: Prescription statistics including most prescribed drugs

### 4. Doctor Workload
- **URL**: `/analytics/doctor-workload`
- **Method**: GET
- **Response**: Workload statistics for each doctor

## Error Handling

The service handles various error conditions:
- Invalid API token
- Main API unavailability
- Invalid parameters
- Data processing errors

## Dependencies

- Flask 2.0.1
- Requests 2.26.0
- Pandas 2.1.4
- NumPy 1.24.3
- Matplotlib 3.7.1
- Python-dotenv 0.19.0 
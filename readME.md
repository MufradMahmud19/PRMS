# 🏥 PRMS.fi (Patient Record Management System)

A comprehensive healthcare management system with a FastAPI backend, React frontend, and analytics service. This project was developed as part of a group coursework.

## 👥 Group Members

- **Mufrad Mahmud** – [mufrad.mahmud@student.oulu.fi](mailto:mufrad.mahmud@student.oulu.fi)
- **Md. Noman** – [Md.Noman@student.oulu.fi](mailto:Md.Noman@student.oulu.fi)  
- **Siraj Us Salekin** – [Siraj.Salekin@student.oulu.fi](mailto:Siraj.Salekin@student.oulu.fi)

## 🌟 Overview

A comprehensive web application designed to streamline patient record management for healthcare professionals, providing an intuitive and efficient way to handle patient information, medical visits, prescriptions, and reports.

## 🚀 Key Features

### Backend Features
- Patient data CRUD operations
- Visit history tracking
- Prescription and report management
- Hypermedia controls via HAL (`_links`, `_embedded`)
- Error recovery links
- Swagger UI and automated OpenAPI validation
- Functional and hypermedia testing
- Redis integration for fast access

### Frontend Features
1. **Authentication System**
   - Secure user login mechanism
   - JWT-based authentication
   - Protected routes
   - Persistent login state

2. **Patient Management**
   - Comprehensive patient tracking
   - Add/Edit/Delete patient records
   - Detailed patient view with multiple tabs
   - Quick search and filter capabilities

3. **Visits Management**
   - Record and track patient visits
   - Add new visit entries
   - View visit history
   - Doctor-specific visit logs

4. **Prescription Management**
   - Create and track prescriptions
   - View prescription history
   - Associate prescriptions with visits
   - Detailed prescription tracking

5. **Medical Reports**
   - Generate and store medical reports
   - Multiple report type support
   - Easy report creation interface
   - Comprehensive report tracking

6. **Analytics Dashboard**
   - Real-time patient statistics
   - Visit trends analysis
   - Prescription patterns
   - Doctor workload monitoring

## 📁 Project Structure

```plaintext
├── app/                    # Main API
│   ├── main.py
│   ├── models/
│   ├── routes/
│   └── hateoas.py
├── medical_analytics_service/  # Analytics Service
│   ├── app.py
│   └── static/
├── client/                # React Frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── tests/
│   ├── test_patient_data.py
│   ├── test_patient_history.py
│   └── test_prescription.py
├── profiles/
│   └── hospital-profile.json
├── requirements.txt
└── README.md
```

## ⚙️ Installation

### Backend Setup
```bash
# Clone repository
git clone https://github.com/yourusername/PRMS.git
cd PRMS

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Edit .env file with your settings
```

### Frontend Setup
```bash
cd client
npm install
npm start
```

### Analytics Service Setup
```bash
cd medical_analytics_service
pip install -r requirements.txt
# Configure .env file with API token
```

## 🔐 Environment Variables

### Main API (.env)
```bash
REDIS_HOST=your-redis-host
REDIS_PORT=your-redis-port
REDIS_PASSWORD=your-redis-password
```


### Analytics Service (.env)
```bash
API_BASE_URL=http://localhost:5001/api
API_TOKEN=your-jwt-token
```


## 🚦 Running the Services

### Main API
```bash
uvicorn main:app --reload
# Visit: http://127.0.0.1:5001/docs for Swagger UI
```

### Analytics Service
```bash
python app.py
# Visit: http://localhost:5002 for dashboard
```

### Frontend
```bash
cd client
npm start
# Visit: http://localhost:3000
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_patient_data.py::test_create_patient
```

## 📘 API Documentation

### Main Endpoints
|**Resource**|**Method**|**Endpoint**|**Description**|
|:----------:|:--------:|:----------:|:-------------:|
|Patients|POST|/patients|Create patient|
|Patients|GET|/patients/{id}|Get patient|
|Visits|POST|/visits|Add visit|
|Visits|GET|/visits/{id}|Get visit|
|Prescriptions|POST|/prescriptions|Create prescription|
|Prescriptions|GET|/prescriptions/{id}|Get prescription|

### Analytics Endpoints
|**Endpoint**|**Description**|
|:----------:|:-------------:|
|/analytics/patient-stats|Patient statistics|
|/analytics/visit-trends|Visit analysis|
|/analytics/prescription-analysis|Prescription patterns|
|/analytics/doctor-workload|Doctor performance|

## 🔍 Example API Usage

```bash
# Create Visit
curl -X POST "http://localhost:5001/api/visits" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer your-token" \
-d '{
  "patient_id": "123",
  "visit_date": "2024-03-20",
  "doctor_id": "D100",
  "diagnosis": "Flu"
}'
```

## 🛠️ Technical Stack

### Backend
- FastAPI
- Redis
- JWT Authentication
- HAL+JSON

### Frontend
- React.js
- React Router
- React Bootstrap
- JWT Authentication

### Analytics Service
- Flask
- Chart.js
- Pandas
- NumPy

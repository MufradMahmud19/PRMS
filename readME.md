# 🏥 PRMS.fi (Patient Record Management System)

A hypermedia-driven patient management system built using FastAPI, Redis, and robust testing tools. This project was developed as part of a group coursework.

## 👥 Group Members

- **Md. Noman** – [Md.Noman@student.oulu.fi](mailto:Md.Noman@student.oulu.fi)  
- **Siraj Us Salekin** – [Siraj.Salekin@student.oulu.fi](mailto:Siraj.Salekin@student.oulu.fi)  
- **Mufrad Mahmud** – [mufrad.mahmud@student.oulu.fi](mailto:mufrad.mahmud@student.oulu.fi)

---

## 🚀 Features

- Patient data CRUD operations
- Visit history tracking
- Prescription and report management
- Hypermedia controls via HAL (`_links`, `_embedded`)
- Error recovery links
- Swagger UI and automated OpenAPI validation
- Functional and hypermedia testing
- Redis integration for fast access

---

## 📁 Project Structure

```plaintext
├── app/
│   ├── main.py
│   ├── models/
│   ├── routes/
│   └── hateoas.py
├── tests/
│   ├── test_patient_data.py
│   ├── test_patient_history.py
│   ├── test_prescription.py
│   ├── test_utils.py
│   └── run_tests.sh
├── profiles/
│   └── hospital-profile.json
├── requirements.txt
├── test_requirements.txt
└── README.md
```


### ⚙️ Installation

```bash
git clone https://github.com/yourusername/PatientHistory.git
cd PatientHistory

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 🔐 Environment Variables
## Edit `DBConnection.py`:

```python
redis = get_redis_connection(
    host="your-redis-host",
    port=your-redis-port,
    password="your-redis-password",
    decode_responses=True
)
```

### 🚦 Running the API

```bash
uvicorn main:app --reload
# Visit: http://127.0.0.1:8000/docs for Swagger UI
```

### 🛠️ Deployment Guide

```bash
# Seed and run with Gunicorn
flask init-db
flask seed-db
gunicorn --bind :5000 run:app
```

### 🧪 Functional Testing Suite

```bash
# Run all tests
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_patient_data.py::test_create_patient
```

### ✔️ Coverage Highlights
|**Type**|**Tests**|**Purpose**|
|:Link Validation:|:28:|:Verifies _links correctness:|
|:Error Recovery:|:15:|:Ensures helpful links on 4xx/5xx:|
|:State Validation:|:12:|:Confirms valid transitions:|

### 🌐 Hypermedia API
- Media Type: `application/hal+json`

Example:
  ```json
  {
  "_links": {
    "self": {"href": "/patients/123", "method": "GET"},
    "hospital:visits": {"href": "/visits?patient=123", "method": "GET"}
  }
 }
```

### 🔄 Error Response Example
```json
{
  "error": "Patient not found",
  "_links": {
    "hospital:search": {
      "href": "/patients?q={name}",
      "templated": true
    }
  }
}
```

### 📘 API Examples

## Patient
|Method|Endpoint|Description|
|POST|/patients|Create patient|
|GET|/patients/{id}|Get patient|
|PUT|/patients/{id}|Update patient|
|DELETE|/patients/{id}|Delete patient|

## Visit
|Method|Endpoint|Description|
|POST	|/patient_visit	|Add visit|
|GET	|/patient_visit/{id}|	Get visit history|
|PUT	|/patient_visit/{id}|	Update visit|
|DELETE	|/patient_visit/{id}	|Delete visit|

## Prescription
|Method	|Endpoint|	Description|
|POST	|/prescription/|	Create prescription|
|GET	|/prescription/{id}|	Get prescription|
|PUT	|/prescription/{id}|	Update prescription|
|DELETE	|/prescription/{id}|	Delete prescription|

### 🔍 Example cURL (Create Visit)

```bash
curl -X POST "http://127.0.0.1:8000/patient_visit" \
-H "Content-Type: application/json" \
-d '{
  "patient_id": "01JN9JJVXW8Z3Y5Z8BMD4YCHM7",
  "visit_date": "2025-02-09",
  "doctor_id": "D100",
  "diagnosis": "Flu",
  "prescription_id": "PRESC5678",
  "notes": "Rest for 3 days"
}'
```

### 🧠 Hypermedia Enhancements
## Custom Relations
|Relation|	Type|	Purpose|
|hospital:prescribe|	Action|	Create prescription|
|hospital:attach-report|	Navigation|	Link reports to visits|
|hospital:patient-timeline|	Collection|	Full history for a patient|

### 🔍 Known Issues & Fixes
- Broken pagination: Fixed with dynamic request.host_url
- Missing 404 recovery: Added hospital:search links
- Invalid state transitions: Validated visit.status before exposing links
- Swagger mismatch: Corrected PATCH vs PUT in docs

### 🧪 Automated Test Script

`run_tests.sh`:

```bash
#!/bin/bash

echo "Running API tests..."
pytest tests/ --cov=app --cov-report=html

echo "Validating hypermedia..."
python -c "from app.hateoas import validate_links; validate_links()"

echo "Testing error cases..."
curl -X GET http://localhost:5000/patients/999 \
  -H 'Accept: application/json' | jq '._links'

```

### 📂 Data Seeding

```bash
flask seed-db
```













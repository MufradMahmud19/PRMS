# Patient API

This project is a **FastAPI-based RESTful API** for managing patient visit histories and prescriptions using **Redis** as the database.

## 🚀 Features
- **Patient Data Records**: Create, retrieve, update, and delete patient.
- **Patient Visit Records**: Create, retrieve, update, and delete patient visit history.
- **Prescription Management**: Store, retrieve, update, and delete prescriptions.
- **Patient Report Management**: Store, retrieve, update, and delete patient report.
- **Redis Integration**: Uses `redis-om` for high-speed database access.
- **CORS Enabled**: Supports cross-origin requests for frontend integration.

## 📌 Installation
### 1️⃣ Clone the repository
```sh
git clone https://github.com/yourusername/PatientHistory.git
cd PatientHistory
```

### 2️⃣ Create a Virtual Environment (Optional but Recommended)
```sh
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

## 🛠️ Environment Variables
Set up the Redis connection details in DBConnection.py:

```sh
redis = get_redis_connection(
    host="your-redis-host",
    port=your-redis-port,
    password="your-redis-password",
    decode_responses=True
)
```
## 🚦 Running the API
### 1️⃣ Start FastAPI Server
```sh
uvicorn main:app --reload
````
By default, the server runs at http://127.0.0.1:8000

### 2️⃣ Test API Endpoints
You can test the API using:

Swagger UI: Open http://127.0.0.1:8000/docs
Postman / curl requests.

## 🏥 API Endpoints (Some Examples)
### 📌 Patient Visit

|  Method       | Endpoint | Description |
|:-------------------: |:------------:|:--------------------:|
|POST       |     /patient_visit         |        Create a new patient visit              |
|GET       |        /patient_visit/{patient_id}      |          Retrieve patient visit history            |
|PUT       |        /patient_visit/{pk}      |            Update a patient visit record          |
|DELETE       |      /patient_visit/{pk}        |          Delete a patient visit record            |

### 📌 Prescription

|  Method       | Endpoint | Description |
|:-------------------: |:------------:|:--------------------:|
|POST       |     /prescription/         |        Create a new prescription              |
|GET       |        /prescription/{prescription_id}      |          Retrieve a prescription            |
|PUT       |        /prescription/{pk}      |            Update a prescription          |
|DELETE       |      /prescription/{pk}        |         Delete a prescription            |

## 🔥 Example Request (Create Patient Visit)

```sh
curl -X POST "http://127.0.0.1:8000/patient_visit" \
     -H "Content-Type: application/json" \
     -d '{
          "patient_id": "12345",
          "visit_date": "2025-02-09",
          "doctor_id": "D100",
          "diagnosis": "Flu",
          "prescription_id": "P5678",
          "notes": "Rest for 3 days"
      }'
````

## 🗄️ Database Setup

By default, Redis stores data automatically. If using a pre-populated Redis DB (dump.rdb), restore it by placing it in your Redis directory and restarting Redis.







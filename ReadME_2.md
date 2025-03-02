# 🛠️ RESTful API Testing for Patient Management System

This repository contains **functional tests** for the **Patient Management API**, covering:
- **Patient Data**
- **Patient Visit History**
- **Prescriptions**  

The tests validate:

✅ API endpoints' functionality

✅ Correct handling of valid/invalid requests

✅ Proper response codes and error messages  

---

## 📌 Project Structure
tests/ │── test_patient_data.py # Tests for Patient API │── test_patient_history.py # Tests for Visit History API │── test_prescription.py # Tests for Prescription API │── test_utils.py # Helper functions │── test_data.json # Sample test data │── run_tests.sh # Shell script to execute tests │── README.md # Documentation


---

## 📦 Dependencies
Ensure the following Python libraries are installed:
```sh
pip install fastapi
pip install "uvicorn[standard]"
pip install redis-om
pip install fastapi[all]
pip install pytest requests
pip install pylint
```

## 🚀 Running the Tests
### 1️⃣ Start the APIs

Run the Patient API:
```sh
uvicorn main:app --reload --port 8000
```

Run the Patient History API:
```sh
uvicorn main:app --reload --port 8001
```

### 2️⃣ Run Functional Tests
Execute all tests:
```sh
pytest tests/
```

Run a specific test file:
```sh
pytest tests/PatientData/main.py
```

Run a single test:
```sh
pytest tests/test_patient_data.py::test_create_patient
```

## 🏥 API Testing Details
### 🔹 Patient Data API

|  Method       | Endpoint | Description |
|:-------------------: |:------------:|:--------------------:|
|POST       |     /patients         |            Create a new patient          |
|GET       |       /patients/{patient_id}       |         Retrieve patient details             |
|PUT       |        /patients/{patient_id}      |          Update patient details            |
|DELETE       |       /patients/{patient_id}       |           Delete a patient record           |

Example Test (Create Patient)

In POSTMAN:

127.0.0.1:8000/patients

Method: POST
```sh
{
    "person_id_hashed": "1A2B3C",
    "full_name": "John Doe",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "1234567890",
    "address": "123 Main St",
    "postal_code": "12345",
    "street_number": "123",
    "street_name": "Main St",
    "gender_code": "M",
    "gender": "Male",
    "birth_year": 1990,
    "birth_date": "1990-01-01",
    "patient_id": "patient123"
}
```

### 🔹 Patient Visit API

|  Method       | Endpoint | Description |
|:-------------------: |:------------:|:--------------------:|
|POST       |     /patient_visit         |           Create a new visit          |
|GET       |       /patient_visit/{patient_id}       |         Retrieve visit history             |
|PUT       |        /patient_visit/{visit_id}      |          Update a visit record           |
|DELETE       |       /patient_visit/{visit_id}       |           Delete a visit record          |

Some Example Test (Patient Visit)

In POSTMAN:

Retrieve patient visit

http://127.0.0.1:8001/patient_visit

METHOD: GET

```sh
{
  "id": "<PASTE_THE_PATIENT_ID_HERE>",
  "gender_code": "M",
  "gender": "Male",
  "visit_date": "2025-01-23",
  "doctor_id": "D123",
  "diagnosis": "Flu",
  "prescription_id": "PRESC123",
  "notes": "Patient has mild fever."
}
```

Update Patient Visit

http://127.0.0.1:8001/patient_visit/<PASTE_VISIT_ID(pk of visit history)>

METHOD: PUT

```sh
{
  "patient_id": "<PASTE_PATIENT_ID>",
  "visit_date": "2025-02-01",
  "doctor_id": "D124",
  "diagnosis": "Updated diagnosis",
  "prescription_id": "PRESC456",
  "notes": "Updated visit details."
}
```

### 🔹 Prescription API

|  Method       | Endpoint | Description |
|:-------------------: |:------------:|:--------------------:|
|POST       |     /prescription/         |           Create a prescription          |
|GET       |       /prescription/{prescription_id}       |         Retrieve a prescription             |
|PUT       |        /prescription/{prescription_id}      |          Update a prescription          |
|DELETE       |       /prescription/{prescription_id}       |           Delete a prescription          |

Example Test (Create Prescription)

In POSTMAN:

Create a Prescription

METHOD: POST

http://127.0.0.1:8001/prescription/

```sh
{
  "prescription_id": "PRESC001",
  "doctor_id": "D123",
  "drug_name": "Paracetamol",
  "drug_power": "500mg",
  "intake_duration": "5 days",
  "intake_schedule": "After meals"
}
```

## 🛑 Error Handling Tested

✅ Invalid Patient ID → 404 Not Found

✅ Missing Required Fields → 422 Unprocessable Entity

✅ Duplicate Entries → 400 Bad Request

✅ Invalid Date Format → 422 Validation Error


## Some Observations from Testing

- Some GET requests for patient visits returned errors due to incorrect patient_id handling.
- Validation errors for incorrect data types were caught (e.g., non-numeric phone numbers).
- Edge cases, such as duplicate entries and invalid IDs, were handled effectively.






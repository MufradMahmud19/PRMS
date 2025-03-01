"""
main.py
This script performs data processing for patient of the  hospital .
Author: Noman
Date: February 27, 2025
"""
import time
import hashlib
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection,HashModel,Field

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host='redis-13980.c339.eu-west-3-1.ec2.redns.redis-cloud.com',
    port=13980,
    password='A9EAM68RA1HgkYsP4jxFQctXE5ZRuaiP',
    decode_responses=True
)

class Patient(HashModel):
    """This class act as model for patients data which saved directly in redis."""
    person_id_hashed: str = Field(index=True)
    full_name: str
    first_name: str
    last_name: str
    phone_number: str
    address: str
    postal_code: str
    street_number: str
    street_name: str
    gender_code: str
    gender: str
    birth_year: str
    birth_date: str
    patient_id: str
    time: str = time.strftime("%Y-%m-%d %H:%M:%S")

    # pylint: disable=too-few-public-methods
    class Meta:
        """Meta class for the model."""
        database = redis

@app.post('/patients')
def create_patient(patient: Patient):
    """Create a new patient record."""
    # Hash the person_id_hashed
    patient.person_id_hashed = hashlib.sha256(patient.person_id_hashed.encode()).hexdigest()
    # Check if a patient with the same person_id_hashed already exists
    existing_patients = redis.ft().search(f"@person_id_hashed:{patient.person_id_hashed}").docs
    if existing_patients == []:
        patient.save()
    return patient

@app.get('/patients')
def all_patients():
    """Return all patients."""
    return [format_patient(pk) for pk in Patient.all_pks()]
@app.get('/patients/{pk}')
def get_product(pk: str):
    """Return a single patient."""
    try:
        return format_patient(pk)
    except KeyError:
        return {"message": "No patient found with the given key"}

@app.delete('/patients/{pk}')
def delete_product(pk: str):
    """Delete a patient."""
    try:
        Patient.delete(pk)
        return {"message": "Patient deleted successfully"}
    except KeyError:
        return {"message": "No patient found with the given key or already deleted"}

@app.get("/search/{value}")
def search_in_redis(value: str):
    """
    Search Redis data using a key:value format and return all matching records.

    Args:
        value (str): The input in the format key:value.

    Returns:
        list: All matching records or an error message.
    """
    try:
        # Parse the input value to extract key and value
        if ":" not in value:
            raise HTTPException(
                status_code=400,
                detail="Invalid format. Use key:value format."
            )
        key, value = value.split(":", 1)
        matches = []

        # Use Redis Scan to iterate over keys matching the model prefix
        for key_id in redis.scan_iter(match=f"{value}:*"):
            # Retrieve the hash stored at the key
            record = redis.hgetall(key_id)

            # Check if the provided key-value pair matches the record
            if key in record and record[key] == value:
                matches.append(record)

        if not matches:
            raise HTTPException(status_code=404, detail="No matching records found.")

        return matches

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error occurred: {str(e)}") from e
def format_patient(pk: str):
    """Return a formatted patient."""
    patient = Patient.get(pk)
    return {
        'id': patient.pk,
        'person_id_hashed': patient.person_id_hashed,
        'full_name': patient.full_name,
        'first_name': patient.first_name,
        'last_name': patient.last_name,
        'phone_number': patient.phone_number,
        'address': patient.address,
        'postal_code': patient.postal_code,
        'street_number': patient.street_number,
        'street_name': patient.street_name,
        'gender_code': patient.gender_code,
        'gender': patient.gender,
        'birth_year': patient.birth_year,
        'birth_date': patient.birth_date,
        'patient_id': patient.patient_id
    }

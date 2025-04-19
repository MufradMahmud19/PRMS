"""This module contains the router for the patient history service"""
import time
import httpx
from starlette.requests import Request
from fastapi import HTTPException, APIRouter
from schemas import PatientVisitHistory, Prescription

history_router = APIRouter()

@history_router.post("/patient_visit")
async def create_patient_visit(request: Request, patient_visit: PatientVisitHistory):
    """Create a new patient visit record."""
    body = await request.json()

    async with httpx.AsyncClient() as client:
        req = await client.get("http://127.0.0.1:8000/patients/%s" % body["patient_id"], timeout=5)

    if req.status_code != 200:
        raise HTTPException(status_code=req.status_code, detail="Patient not found")

    patient = req.json()
    patient_visit = PatientVisitHistory(
        patient_id=body['patient_id'],
        full_name=patient['full_name'],
        first_name=patient['first_name'],
        last_name=patient['last_name'],
        phone_number=patient['phone_number'],
        address=patient['address'],
        postal_code=patient['postal_code'],
        street_number=patient['street_number'],
        street_name=patient['street_name'],
        gender_code=body['gender_code'],
        gender=body['gender'],
        visit_date=body['visit_date'],
        doctor_id=body['doctor_id'],
        diagnosis=body['diagnosis'],
        prescription_id=body['prescription_id'],
        notes=body['notes'],
        created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
    )
    
    patient_visit.save()
    return patient_visit

@history_router.get("/patient_visit/{patient_id}")
async def get_patient_visit(patient_id: str):
    """Get a patient visit history by patient ID."""
    patient_visits = PatientVisitHistory.find(PatientVisitHistory.patient_id == patient_id).all()
    if not patient_visits:
        raise HTTPException(status_code=404, detail="Patient visit history not found")
    return patient_visits

@history_router.put("/patient_visit/{pk}")
async def update_patient_visit(pk: str, patient_visit: PatientVisitHistory):
    """Update a patient visit record."""
    existing_visit = PatientVisitHistory.get(pk)
    if not existing_visit:
        raise HTTPException(status_code=404, detail="Patient visit history not found")
    existing_visit.update(**patient_visit.dict())
    return existing_visit

@history_router.delete("/patient_visit/{pk}")
async def delete_patient_visit(pk: str):
    """Delete a patient visit record."""
    patient_visit = PatientVisitHistory.get(pk)
    if not patient_visit:
        raise HTTPException(status_code=404, detail="Patient visit history not found")
    patient_visit.delete()
    return {"message": "Patient visit history deleted successfully"}

@history_router.post("/prescription/")
async def create_prescription(prescription: Prescription):
    """Create a new prescription record."""
    prescription.save()
    return prescription

@history_router.get("/prescription/{prescription_id}")
async def get_prescription(prescription_id: str):
    """Get a prescription by ID."""
    prescription = Prescription.get(prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

@history_router.put("/prescription/{pk}")
async def update_prescription(pk: str, prescription: Prescription):
    """Update a prescription record."""
    existing_prescription = Prescription.get(pk)
    if not existing_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    existing_prescription.update(**prescription.dict())
    return existing_prescription

@history_router.delete("/prescription/{pk}")
async def delete_prescription(pk: str):
    """Delete a prescription record."""
    prescription = Prescription.get(pk)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    prescription.delete()
    return {"message": "Prescription deleted successfully"}

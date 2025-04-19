""" This module defines the schema for the PatientVisitHistory and Prescription models. """
import time
from redis_om import HashModel
from DBConnection import redis

# pylint: disable=too-few-public-methods
class PatientVisitHistory(HashModel):
    """Model for storing patient visit history."""
    patient_id: str  # Reference to the patient
    visit_date: str  # Date of the visit (e.g., '2025-01-23')
    doctor_id: str  # ID of the doctor
    diagnosis: str  # Diagnosis details
    prescription_id: str  # ID of the prescription associated with the visit
    notes: str  # Additional notes or observations
    created_at: str = time.strftime("%Y-%m-%d %H:%M:%S")  # Record creation timestamp

    class Meta:
        """Meta class for the model."""
        database = redis  # Use the Redis connection

# pylint: disable=too-few-public-methods
class Prescription(HashModel):
    """Model for storing prescription details."""
    prescription_id: str  # Unique identifier for the prescription
    doctor_id: str  # ID of the doctor who prescribed it
    drug_name: str  # Name of the drug
    drug_power: str  # Power of the drug (e.g., "500mg")
    intake_duration: str  # Duration of intake (e.g., "7 days")
    intake_schedule: str  # When to take the drug (e.g., "After meals")
    created_at: str = time.strftime("%Y-%m-%d %H:%M:%S")  # Record creation timestamp

    class Meta:
        """Meta class for the model"""
        database = redis  # Use the Redis connection

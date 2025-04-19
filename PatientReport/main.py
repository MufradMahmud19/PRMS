"""
Report Management API
This API provides endpoints to manage reports related to patient data.
Author: Noman
Date: March 1, 2025
"""

import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel, Field

# Initialize FastAPI app
app = FastAPI(debug=True)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

# Redis connection
redis = get_redis_connection(
    host='redis-13980.c339.eu-west-3-1.ec2.redns.redis-cloud.com',
    port=13980,
    password='A9EAM68RA1HgkYsP4jxFQctXE5ZRuaiP',
    decode_responses=True
)

# Pylint directive to ignore certain warnings
# pylint: disable=too-few-public-methods, missing-class-docstring, missing-function-docstring

class Report(HashModel):
    """This class acts as a model for reports stored in Redis."""
    patient_id: str = Field(index=True)
    title: str
    content: str
    remarks: str
    status: str
    created_at: str = time.strftime("%Y-%m-%d %H:%M:%S")

    # pylint: disable=too-few-public-methods
    class Meta:
        """Meta class for the model."""
        database = redis

@app.post('/reports')
def create_report(report: Report):
    """Create a new report record."""
    report.save()
    return report

@app.get('/reports')
def get_all_reports():
    """Retrieve all reports."""
    return [Report.get(pk) for pk in Report.all_pks()]

@app.get('/reports/{report_id}')
def get_report(report_id: str):
    """Retrieve a specific report by its unique ID."""
    try:
        return Report.get(report_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Report not found") from exc

@app.get('/reports/patient/{patient_id}')
def get_reports_by_patient(patient_id: str):
    """Retrieve all reports for a specific patient."""
    return [Report.get(pk) for pk in Report.all_pks() if Report.get(pk).patient_id == patient_id]

@app.get('/reports/timeline')
def get_reports_by_timeline(start_date: str, end_date: str):
    """Retrieve reports within a specific time range."""
    return [
        Report.get(pk) for pk in Report.all_pks()
        if start_date <= Report.get(pk).created_at <= end_date
    ]

@app.get('/reports/patient/{patient_id}/timeline')
def get_patient_reports_by_timeline(patient_id: str, start_date: str, end_date: str):
    """Retrieve reports for a single patient within a specific timeline."""
    return [
        report
         for pk in Report.all_pks()
         if (report := Report.get(pk)).patient_id == patient_id
         and start_date <= report.created_at <= end_date
    ]

@app.delete('/reports/{report_id}')
def delete_report(report_id: str):
    """Delete a report by its unique ID."""
    try:
        Report.delete(report_id)
        return {"message": "Report deleted successfully"}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Report not found") from exc

@app.get('/reports/search/{query}')
def search_reports(query: str):
    """Search for reports based on specific criteria."""
    return [
        Report.get(pk) for pk in Report.all_pks()
        if query in Report.get(pk).title
        or query in Report.get(pk).status]

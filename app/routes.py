from flask import request, jsonify, Blueprint, abort  # type: ignore
from app.models import Patient, Visit, Prescription, Report, User
from app.hateoas import Hateoas
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity  # type: ignore
from .app_extensions import db  # type: ignore
from datetime import datetime
from app.auth import create_token

bp = Blueprint('api', __name__)

# ------------------- Patient Routes ------------------- #

@bp.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    hateoas = Hateoas(request.host_url)
    patient = Patient.query.get_or_404(patient_id)
    return jsonify({
        "data": {
            "name": patient.name,
            "age": patient.age,
            "contact": patient.contact_info
        },
        "_links": hateoas.patient_links(patient_id)
    })

@bp.route('/patients', methods=['POST'])
def create_patient():
    data = request.get_json()
    patient = Patient(name=data['name'], age=data['age'], contact_info=data.get('contact_info', ''))
    db.session.add(patient)
    db.session.commit()
    return jsonify({'message': 'Patient created', 'patient_id': patient.patient_id}), 201

@bp.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json()
    patient.name = data.get('name', patient.name)
    patient.age = data.get('age', patient.age)
    patient.contact_info = data.get('contact_info', patient.contact_info)
    db.session.commit()
    return jsonify({'message': 'Patient updated'})

@bp.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'message': 'Patient deleted'})


# ------------------- Visit Routes ------------------- #

@bp.route('/visits/<int:visit_id>', methods=['GET'])
def get_visit(visit_id):
    hateoas = Hateoas(request.host_url)
    visit = Visit.query.get_or_404(visit_id)
    return jsonify({
        "data": {
            "date": visit.visit_date.isoformat(),
            "diagnosis": visit.diagnosis,
            "doctor": visit.doctor.username
        },
        "_links": hateoas.visit_links(visit_id)
    })

@bp.route('/visits', methods=['POST'])
def create_visit():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        visit_date = datetime.fromisoformat(data['visit_date'].replace('Z', '+00:00'))
    except (KeyError, ValueError):
        visit_date = datetime.now()

    visit = Visit(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        visit_date=visit_date,
        diagnosis=data.get('diagnosis', '')
    )
    db.session.add(visit)
    db.session.commit()
    return jsonify({'message': 'Visit created', 'visit_id': visit.visit_id}), 201

@bp.route('/visits/<int:visit_id>', methods=['PUT'])
def update_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    data = request.get_json()
    visit.diagnosis = data.get('diagnosis', visit.diagnosis)
    db.session.commit()
    return jsonify({'message': 'Visit updated'})

@bp.route('/visits/<int:visit_id>', methods=['DELETE'])
def delete_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    db.session.delete(visit)
    db.session.commit()
    return jsonify({'message': 'Visit deleted'})


# ------------------- Prescription Routes ------------------- #

@bp.route('/prescriptions', methods=['POST'])
def create_prescription():
    data = request.get_json()
    prescription = Prescription(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        visit_id=data.get('visit_id'),
        drug_name=data['drug_name'],
        dosage=data['dosage'],
        duration=data['duration']
    )
    db.session.add(prescription)
    db.session.commit()
    return jsonify({'message': 'Prescription created', 'prescription_id': prescription.prescription_id}), 201

@bp.route('/prescriptions/<int:prescription_id>', methods=['PUT'])
def update_prescription(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)
    data = request.get_json()
    prescription.drug_name = data.get('drug_name', prescription.drug_name)
    prescription.dosage = data.get('dosage', prescription.dosage)
    prescription.duration = data.get('duration', prescription.duration)
    db.session.commit()
    return jsonify({'message': 'Prescription updated'})

@bp.route('/prescriptions/<int:prescription_id>', methods=['DELETE'])
def delete_prescription(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)
    db.session.delete(prescription)
    db.session.commit()
    return jsonify({'message': 'Prescription deleted'})


# ------------------- Report Routes ------------------- #

@bp.route('/reports', methods=['POST'])
def create_report():
    data = request.get_json()
    report = Report(
        patient_id=data['patient_id'],
        report_type=data['report_type'],
        report_data=data['report_data']
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({'message': 'Report created', 'report_id': report.report_id}), 201

@bp.route('/reports/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    report = Report.query.get_or_404(report_id)
    data = request.get_json()
    report.report_type = data.get('report_type', report.report_type)
    report.report_data = data.get('report_data', report.report_data)
    db.session.commit()
    return jsonify({'message': 'Report updated'})

@bp.route('/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    return jsonify({'message': 'Report deleted'})


# ------------------- Auth Routes ------------------- #

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return {'error': 'Missing username or password'}, 400
        
        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            # Create a token with just the user_id
            token = create_token(user)
            print(f"Created token: {token}")  # Debug output
            return {
                'access_token': token,
                'user': user.to_dict()
            }, 200
        return {'error': 'Invalid credentials'}, 401
    except Exception as e:
        print(f"Login error: {str(e)}")  # For debugging
        return {'error': 'Internal server error'}, 500

@bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    try:
        current_user_id = get_jwt_identity()
        print(f"Current user ID: {current_user_id}")  # Debug output
        user = User.query.get(current_user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return {'user': user.to_dict()}
    except Exception as e:
        print(f"Protected route error: {str(e)}")  # For debugging
        return {'error': 'Internal server error'}, 500

# ------------------- Get All Patients ------------------- #
@bp.route('/patients', methods=['GET'])
def get_all_patients():
    patients = Patient.query.all()
    return jsonify([{
        "patient_id": p.patient_id,
        "name": p.name,
        "age": p.age,
        "contact_info": p.contact_info
    } for p in patients])

# ------------------- Get All Visits ------------------- #
@bp.route('/visits', methods=['GET'])
def get_all_visits():
    visits = Visit.query.all()
    return jsonify([{
        "visit_id": v.visit_id,
        "date": v.visit_date.isoformat(),
        "diagnosis": v.diagnosis,
        "doctor_id": v.doctor_id,
        "patient_id": v.patient_id
    } for v in visits])

# ------------------- Get All Prescriptions ------------------- #
@bp.route('/prescriptions', methods=['GET'])
def get_all_prescriptions():
    prescriptions = Prescription.query.all()
    return jsonify([{
        "prescription_id": p.prescription_id,
        "drug_name": p.drug_name,
        "dosage": p.dosage,
        "duration": p.duration,
        "patient_id": p.patient_id,
        "doctor_id": p.doctor_id,
        "visit_id": p.visit_id
    } for p in prescriptions])

# ------------------- Get All Reports ------------------- #
@bp.route('/reports', methods=['GET'])
def get_all_reports():
    reports = Report.query.all()
    return jsonify([{
        "report_id": r.report_id,
        "report_type": r.report_type,
        "report_data": r.report_data,
        "patient_id": r.patient_id
    } for r in reports])
from flask import request, jsonify, Blueprint, abort, current_app, session, render_template  # type: ignore
from app.models import Patient, Visit, Prescription, Report, User
from app.hateoas import Hateoas
from .app_extensions import db  # type: ignore
from datetime import datetime
from app.auth import login_required, create_session, get_current_user, logout, jwt_required
from .cache_utils import cache_response, invalidate_cache
import traceback

bp = Blueprint('api', __name__, url_prefix='/api')

# Welcome route
@bp.route('/', methods=['GET'])
def welcome():
    return jsonify({
        'message': 'Welcome to Patient Record Management System (PRMS)',
        'version': '1.0.0',
        'description': 'A comprehensive system for managing patient records, visits, and prescriptions',
        '_links': {
            'self': {
                'href': '/',
                'method': 'GET'
            },
            'api_docs': {
                'href': '/api/docs',
                'method': 'GET'
            },
            'patients': {
                'href': '/api/patients',
                'method': 'GET'
            },
            'login': {
                'href': '/api/login',
                'method': 'POST'
            }
        }
    })

# Handle CORS preflight requests
@bp.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

# ------------------- Auth Routes ------------------- #

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        if 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Missing username or password'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 401
        if not user.check_password(data['password']):
            return jsonify({'error': 'Invalid password'}), 401
            
        user_data = create_session(user)
        return jsonify({
            'message': 'Login successful',
            'access_token': user_data['access_token'],
            'user': user_data['user']
        }), 200
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout_route():
    return jsonify({'message': 'Logged out successfully'}), 200

# ------------------- Patient Routes ------------------- #

@bp.route('/patients', methods=['GET'])
@jwt_required()
@cache_response(timeout=60)  # Reduced cache timeout to 1 minute
def get_all_patients():
    try:
        patients = Patient.query.all()
        return jsonify([patient.to_dict() for patient in patients])
    except Exception as e:
        current_app.logger.error(f"Error getting patients: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/patients', methods=['POST'])
@jwt_required()
def create_patient():
    try:
        data = request.get_json()
        
        # Check required fields
        required_fields = ['name', 'age', 'contact_info']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        new_patient = Patient(
            name=data['name'],
            age=data['age'],
            contact_info=data['contact_info']
        )
        db.session.add(new_patient)
        db.session.commit()
        
        # Invalidate the patients list cache
        invalidate_cache('get_all_patients:():{}')
        
        return jsonify({
            'message': 'Patient created successfully',
            'patient': new_patient.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating patient: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/patients/<int:patient_id>', methods=['GET'])
@login_required
@cache_response(timeout=60)  # Cache for 1 minute instead of 5 minutes
def get_patient(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        return jsonify(patient.to_dict())
    except Exception as e:
        current_app.logger.error(f"Error getting patient: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/patients/<int:patient_id>', methods=['PUT'])
@login_required
def update_patient(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        data = request.get_json()
        patient.name = data.get('name', patient.name)
        patient.age = data.get('age', patient.age)
        patient.contact_info = data.get('contact_info', patient.contact_info)
        db.session.commit()
        
        # Invalidate cache for this patient and patient list
        invalidate_cache(f'get_patient:({patient_id},):{{}}', 'get_all_patients:():{}')
        
        # Return the updated patient data
        return jsonify({
            'message': 'Patient updated successfully',
            'patient': patient.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating patient: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/patients/<int:patient_id>', methods=['DELETE'])
@login_required
def delete_patient(patient_id):
    try:
        patient = Patient.query.get_or_404(patient_id)
        db.session.delete(patient)
        db.session.commit()
        
        # Invalidate cache for this patient and patient list
        invalidate_cache(f'get_patient:({patient_id},):{{}}', 'get_all_patients:():{}')
        
        return jsonify({'message': 'Patient deleted'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting patient: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

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

@bp.route('/static/swagger.json')
def serve_swagger():
    return current_app.send_static_file('swagger.json')
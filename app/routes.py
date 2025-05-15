from flask import request, jsonify, Blueprint, abort, current_app, session, render_template
from app.models import Patient, Visit, Prescription, Report, User
from app.hateoas import Hateoas
from .app_extensions import db
from datetime import datetime
from app.auth import login_required, create_session, get_current_user, logout, jwt_required
from .cache_utils import cache_response, invalidate_cache
import traceback
import json

bp = Blueprint('api', __name__, url_prefix='/api')

# Welcome route
@bp.route('/', methods=['GET'])
@cache_response(timeout=300)  # Cache welcome page for 5 minutes
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

@bp.route('/setup-doctors', methods=['POST'])
def setup_doctors():
    try:
        # Check if doctors already exist
        existing_doctors = User.query.filter(User.username.in_(['dr_smith', 'dr_smith_2', 'dr_smith_3'])).all()
        if existing_doctors:
            # Delete existing doctors to ensure clean setup
            for doctor in existing_doctors:
                db.session.delete(doctor)
            db.session.commit()

        # Create doctors with specific IDs
        doctors = [
            User(username='dr_smith', role='doctor'),
            User(username='dr_smith_2', role='doctor'),
            User(username='dr_smith_3', role='doctor')
        ]
        
        # Set passwords
        doctors[0].set_password('password123')
        doctors[1].set_password('password1234')
        doctors[2].set_password('password12345')
        
        # Add to database
        for doctor in doctors:
            db.session.add(doctor)
        db.session.commit()
        
        return jsonify({
            'message': 'Doctors created successfully',
            'doctors': [d.to_dict() for d in doctors]
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating doctors: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

# ------------------- Patient Routes ------------------- #

@bp.route('/patients', methods=['GET'])
@jwt_required()
@cache_response(timeout=60)  # Cache for 1 minute
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
@cache_response(timeout=60)  # Cache for 1 minute
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
    except Exception as e:
        db.session.rollback()
        

    # Do cache invalidation outside the db transaction
    try:
        invalidate_cache(f'get_patient:({patient_id},):{{}}', 'get_all_patients:():{}')
    except Exception as e:
        current_app.logger.error(f"Error invalidating cache: {str(e)}")
        # Do NOT return error here — just log and continue
    
    return jsonify({'message': 'Patient deleted'})

@bp.route('/patients/<int:patient_id>/visits', methods=['GET'])
@jwt_required()
@cache_response(timeout=60)  # Cache for 1 minute
def get_patient_visits(patient_id):
    try:
        visits = Visit.query.filter_by(patient_id=patient_id).all()
        return jsonify([{
            'visit_id': visit.visit_id,
            'visit_date': visit.visit_date.isoformat(),
            'doctor': visit.doctor.username,
            'diagnosis': visit.diagnosis,
            'prescriptions': [{
                'prescription_id': p.prescription_id,
                'drug_name': p.drug_name,
                'dosage': p.dosage,
                'duration': p.duration
            } for p in visit.prescriptions]
        } for visit in visits])
    except Exception as e:
        current_app.logger.error(f"Error getting patient visits: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/patients/<int:patient_id>/prescriptions', methods=['GET'])
@jwt_required()
@cache_response(timeout=60)  # Cache for 1 minute
def get_patient_prescriptions(patient_id):
    try:
        prescriptions = Prescription.query.filter_by(patient_id=patient_id).all()
        return jsonify([{
            'prescription_id': p.prescription_id,
            'drug_name': p.drug_name,
            'dosage': p.dosage,
            'duration': p.duration,
            'visit_date': p.visit.visit_date.isoformat() if p.visit else None,
            'doctor': p.prescribing_doctor.username
        } for p in prescriptions])
    except Exception as e:
        current_app.logger.error(f"Error getting patient prescriptions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/patients/<int:patient_id>/reports', methods=['GET'])
@jwt_required()
@cache_response(timeout=60)  # Cache for 1 minute
def get_patient_reports(patient_id):
    try:
        reports = Report.query.filter_by(patient_id=patient_id).all()
        return jsonify([{
            'report_id': r.report_id,
            'report_type': r.report_type,
            'report_data': r.report_data,
            'created_at': r.created_at.isoformat()
        } for r in reports])
    except Exception as e:
        current_app.logger.error(f"Error getting patient reports: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# ------------------- Visit Routes ------------------- #

@bp.route('/visits/<int:visit_id>', methods=['GET'])
@cache_response(timeout=60)  # Cache for 1 minute
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
@jwt_required()
def create_visit():
    try:
        # Log the raw request data for debugging
        raw_data = request.get_data().decode('utf-8', errors='replace')
        current_app.logger.debug(f"Raw request data: {raw_data}")
        
        # Clean the data by removing any BOM, special characters, and normalizing line endings
        cleaned_data = raw_data.replace('\ufeff', '').replace('\r\n', '\n').strip()
        # Remove any non-printable characters
        cleaned_data = ''.join(char for char in cleaned_data if char.isprintable() or char in '\n\r\t')
        
        # Try to parse JSON with detailed error handling
        try:
            # First try with the cleaned data
            data = json.loads(cleaned_data)
        except json.JSONDecodeError as json_error:
            try:
                # If that fails, try with the raw data
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                current_app.logger.error(f"JSON parsing error: {str(json_error)}")
                current_app.logger.error(f"Request content type: {request.content_type}")
                current_app.logger.error(f"Cleaned data: {cleaned_data}")
                return jsonify({
                    'error': f'Invalid JSON format: {str(json_error)}',
                    'content_type': request.content_type,
                    'raw_data': raw_data,
                    'cleaned_data': cleaned_data,
                    'suggestion': 'Please ensure your JSON is properly formatted with no special characters'
                }), 400

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['patient_id', 'doctor_id', 'diagnosis']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate patient exists
        patient = Patient.query.get(data['patient_id'])
        if not patient:
            return jsonify({'error': f'Patient with ID {data["patient_id"]} not found'}), 404

        # Validate doctor exists
        doctor = User.query.get(data['doctor_id'])
        if not doctor:
            return jsonify({'error': f'Doctor with ID {data["doctor_id"]} not found'}), 404

        # Debug the diagnosis value
        current_app.logger.debug(f"Original diagnosis: '{data['diagnosis']}'")
        current_app.logger.debug(f"Diagnosis type: {type(data['diagnosis'])}")
        current_app.logger.debug(f"Diagnosis length: {len(data['diagnosis'])}")
        current_app.logger.debug(f"Diagnosis characters: {[ord(c) for c in data['diagnosis']]}")

        # Ensure diagnosis is properly formatted
        diagnosis = data['diagnosis'].strip()
        if not diagnosis:
            return jsonify({'error': 'Diagnosis cannot be empty'}), 400

        # Debug the cleaned diagnosis value
        current_app.logger.debug(f"Cleaned diagnosis: '{diagnosis}'")
        current_app.logger.debug(f"Cleaned diagnosis type: {type(diagnosis)}")
        current_app.logger.debug(f"Cleaned diagnosis length: {len(diagnosis)}")
        current_app.logger.debug(f"Cleaned diagnosis characters: {[ord(c) for c in diagnosis]}")

        # Create visit with current timestamp
        visit = Visit(
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            visit_date=datetime.now(),  # Automatically use current timestamp
            diagnosis=diagnosis  # Use the properly formatted diagnosis
        )
        db.session.add(visit)
        db.session.commit()

        # Debug the stored diagnosis value
        current_app.logger.debug(f"Stored diagnosis: '{visit.diagnosis}'")
        current_app.logger.debug(f"Stored diagnosis type: {type(visit.diagnosis)}")
        current_app.logger.debug(f"Stored diagnosis length: {len(visit.diagnosis)}")
        current_app.logger.debug(f"Stored diagnosis characters: {[ord(c) for c in visit.diagnosis]}")

        # Invalidate caches
        invalidate_cache(
            f'get_patient_visits:({data["patient_id"]},):{{}}',
            'get_all_visits:():{}'
        )

        # Return the same format as get_all_visits
        response_data = {
            'message': 'Visit created successfully',
            'visit': {
                'visit_id': visit.visit_id,
                'patient_id': visit.patient_id,
                'doctor_id': visit.doctor_id,
                'visit_date': visit.visit_date.isoformat(),
                'diagnosis': visit.diagnosis,  # This should preserve spaces
                'doctor': visit.doctor.username if visit.doctor else None
            }
        }

        # Debug the response data
        current_app.logger.debug(f"Response diagnosis: '{response_data['visit']['diagnosis']}'")
        current_app.logger.debug(f"Response diagnosis type: {type(response_data['visit']['diagnosis'])}")
        current_app.logger.debug(f"Response diagnosis length: {len(response_data['visit']['diagnosis'])}")
        current_app.logger.debug(f"Response diagnosis characters: {[ord(c) for c in response_data['visit']['diagnosis']]}")

        return jsonify(response_data), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating visit: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@bp.route('/visits', methods=['GET'])
@jwt_required()
@cache_response(timeout=60)  # Cache for 1 minute
def get_all_visits():
    try:
        visits = Visit.query.all()
        return jsonify([{
            'visit_id': visit.visit_id,
            'patient_id': visit.patient_id,
            'doctor_id': visit.doctor_id,
            'visit_date': visit.visit_date.isoformat(),
            'diagnosis': visit.diagnosis,  # This should preserve spaces
            'doctor': visit.doctor.username if visit.doctor else None
        } for visit in visits])
    except Exception as e:
        current_app.logger.error(f"Error getting visits: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

# ------------------- Prescription Routes ------------------- #

@bp.route('/prescriptions', methods=['GET'])
@jwt_required()
@cache_response(timeout=60)  # Cache for 1 minute
def get_all_prescriptions():
    try:
        prescriptions = Prescription.query.all()
        return jsonify([prescription.to_dict() for prescription in prescriptions])
    except Exception as e:
        current_app.logger.error(f"Error getting prescriptions: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/prescriptions/<int:prescription_id>', methods=['GET'])
@jwt_required()
def get_prescription_by_id(prescription_id):
    try:
        prescription = Prescription.query.get_or_404(prescription_id)
        return jsonify(prescription.to_dict())
    except Exception as e:
        current_app.logger.error(f"Error fetching prescription: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

      
@bp.route('/prescriptions', methods=['POST'])
@jwt_required()
def create_prescription():
    try:
        # Log the raw request data for debugging
        raw_data = request.get_data().decode('utf-8', errors='replace')
        current_app.logger.debug(f"Raw request data: {raw_data}")
        
        # Clean the data by removing any BOM, special characters, and normalizing line endings
        cleaned_data = raw_data.replace('\ufeff', '').replace('\r\n', '\n').strip()
        # Remove any non-printable characters
        cleaned_data = ''.join(char for char in cleaned_data if char.isprintable() or char in '\n\r\t')
        
        # Try to parse JSON with detailed error handling
        try:
            # First try with the cleaned data
            data = json.loads(cleaned_data)
        except json.JSONDecodeError as json_error:
            try:
                # If that fails, try with the raw data
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                current_app.logger.error(f"JSON parsing error: {str(json_error)}")
                current_app.logger.error(f"Request content type: {request.content_type}")
                current_app.logger.error(f"Cleaned data: {cleaned_data}")
                return jsonify({
                    'error': f'Invalid JSON format: {str(json_error)}',
                    'content_type': request.content_type,
                    'raw_data': raw_data,
                    'cleaned_data': cleaned_data,
                    'suggestion': 'Please ensure your JSON is properly formatted with no special characters'
                }), 400

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['patient_id', 'doctor_id', 'drug_name', 'dosage', 'duration']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate patient exists
        patient = Patient.query.get(data['patient_id'])
        if not patient:
            return jsonify({'error': f'Patient with ID {data["patient_id"]} not found'}), 404

        # Validate doctor exists
        doctor = User.query.get(data['doctor_id'])
        if not doctor:
            return jsonify({'error': f'Doctor with ID {data["doctor_id"]} not found'}), 404

        try:
            # Create a new visit automatically
            visit = Visit(
                patient_id=data['patient_id'],
                doctor_id=data['doctor_id'],
                visit_date=datetime.now(),
                diagnosis=f"Prescription for {data['drug_name']}"
            )
            db.session.add(visit)
            db.session.flush()  # This will get us the visit_id without committing

            # Create prescription with the new visit
            prescription = Prescription(
                patient_id=data['patient_id'],
                doctor_id=data['doctor_id'],
                visit_id=visit.visit_id,  # Use the automatically created visit
                drug_name=data['drug_name'],
                dosage=data['dosage'],
                duration=data['duration']
            )
            db.session.add(prescription)
            db.session.commit()

            # Invalidate caches
            invalidate_cache(
                f'get_patient_prescriptions:({data["patient_id"]},):{{}}',
                'get_all_prescriptions:():{}',
                f'get_patient_visits:({data["patient_id"]},):{{}}',
                'get_all_visits:():{}'
            )

            return jsonify({
                'message': 'Prescription created successfully',
                'prescription': {
                    'prescription_id': prescription.prescription_id,
                    'patient_id': prescription.patient_id,
                    'doctor_id': prescription.doctor_id,
                    'visit_id': prescription.visit_id,
                    'drug_name': prescription.drug_name,
                    'dosage': prescription.dosage,
                    'duration': prescription.duration,
                    'visit_date': visit.visit_date.isoformat(),
                    'doctor': visit.doctor.username if visit.doctor else None
                }
            }), 201
        except Exception as db_error:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(db_error)}")
            current_app.logger.error(traceback.format_exc())
            return jsonify({'error': f'Database error: {str(db_error)}'}), 500

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating prescription: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# ------------------- Report Routes ------------------- #

@bp.route('/reports', methods=['GET'])
@jwt_required()
@cache_response(timeout=60)  # Cache for 1 minute
def get_all_reports():
    try:
        reports = Report.query.all()
        return jsonify([report.to_dict() for report in reports])
    except Exception as e:
        current_app.logger.error(f"Error getting reports: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/reports', methods=['POST'])
@jwt_required()
def create_report():
    try:
        data = request.get_json() or request.form
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['patient_id', 'report_type', 'report_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Create report
        report = Report(
            patient_id=data['patient_id'],
            report_type=data['report_type'],
            report_data=data['report_data']
        )
        db.session.add(report)
        db.session.commit()

        # Invalidate caches
        invalidate_cache(
            f'get_patient_reports:({data["patient_id"]},):{{}}',
            'get_all_reports:():{}'
        )

        return jsonify({
            'message': 'Report created successfully',
            'report': {
                'report_id': report.report_id,
                'report_type': report.report_type,
                'report_data': report.report_data,
                'created_at': report.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating report: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/reports/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    try:
        report = Report.query.get_or_404(report_id)
        db.session.delete(report)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting report: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

    # Do cache invalidation outside the db transaction
    try:
        invalidate_cache(f'get_patient_reports:({report.patient_id},):{{}}', 'get_all_reports:():{}')
    except Exception as e:
        current_app.logger.error(f"Error invalidating cache: {str(e)}")
        # Do NOT return error here — just log and continue

    return jsonify({'message': 'Report deleted successfully'})
@bp.route('/reports/<int:report_id>', methods=['GET'])
@jwt_required()
@cache_response(timeout=60)  # Cache for 1 minute
def get_report(report_id):
    try:
        report = Report.query.get_or_404(report_id)
        return jsonify({
            'report_id': report.report_id,
            'report_type': report.report_type,
            'report_data': report.report_data,
            'created_at': report.created_at.isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error getting report: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


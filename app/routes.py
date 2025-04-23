from flask import request, jsonify, Blueprint # type: ignore
from app.models import Patient, Visit, Prescription, Report, User
from app.hateoas import Hateoas

from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity # type: ignore
from .models import User
from .app_extensions import jwt,db # type: ignore
bp = Blueprint('api', __name__)

@bp .route('/patients/<int:patient_id>', methods=['GET'])
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

@bp.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(username=request.json['username']).first()
    if user and user.check_password(request.json['password']):
        token = create_access_token(identity=user)
        return {'access_token': token}
    return {'error': 'Invalid credentials'}, 401

@bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return {'user_id': current_user.user_id}

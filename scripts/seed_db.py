from app import create_app
from app.models import db, Patient, Visit

app = create_app()

with app.app_context():
    # Clear and recreate
    db.drop_all()
    db.create_all()

    # Sample data
    p1 = Patient(patient_id=1, name="John Doe", age=45)
    v1 = Visit(visit_id=1, patient_id=1, diagnosis="Hypertension")
    
    db.session.add_all([p1, v1])
    db.session.commit()
    print("Database seeded with test data!")

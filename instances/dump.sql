CREATE TABLE user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(50) NOT NULL
);

CREATE TABLE patient (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    contact_info VARCHAR(100)
);

CREATE TABLE visit (
    visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    visit_date DATETIME NOT NULL,
    diagnosis TEXT,
    FOREIGN KEY (patient_id) REFERENCES patient (patient_id),
    FOREIGN KEY (doctor_id) REFERENCES user (user_id)
);

CREATE TABLE prescription (
    prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    visit_id INTEGER,
    drug_name VARCHAR(100) NOT NULL,
    dosage VARCHAR(50) NOT NULL,
    duration INTEGER NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patient (patient_id),
    FOREIGN KEY (doctor_id) REFERENCES user (user_id),
    FOREIGN KEY (visit_id) REFERENCES visit (visit_id)
);

CREATE TABLE report (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    report_data TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patient (patient_id)
);


from flask import request

class Hateoas:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def patient_links(self, patient_id):
        return {
            "self": {"href": f"{self.base_url}/patients/{patient_id}", "method": "GET"},
            "visits": {"href": f"{self.base_url}/visits?patient={patient_id}", "method": "GET"},
            "reports": {"href": f"{self.base_url}/reports?patient={patient_id}", "method": "GET"},
            "prescriptions": {"href": f"{self.base_url}/prescriptions?patient={patient_id}", "method": "GET"}
        }
    
    def visit_links(self, visit_id):
        return {
            "prescribe": {"href": f"{self.base_url}/prescriptions", "method": "POST"},
            "add_report": {"href": f"{self.base_url}/reports", "method": "POST"}
        }

    def error_links(self, error_code):
        base_links = {
            "self": {"href": request.path, "method": request.method},
            "home": {"href": "/", "method": "GET"}
        }
        
        if error_code == 404:
            base_links["hospital:search"] = {
                "href": "/patients?q={search_term}",
                "method": "GET",
                "templated": True
            }
        elif error_code == 400:
            base_links["hospital:validation-help"] = {
                "href": "/docs/validation-rules",
                "method": "GET"
            }
            
        return base_links

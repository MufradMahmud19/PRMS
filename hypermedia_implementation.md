# Hypermedia Implementation

## Media Type: `application/hal+json`
**Reasoning**:  
- Native support for embedded resources (`_embedded`) and links (`_links`)  
- Compatible with JSON tooling while providing hypermedia controls  
- Adopted by healthcare standards like FHIR  

## Custom Link Relations
| Relation | Type | IANA Equivalent | Purpose |
|----------|------|-----------------|---------|
| `hospital:prescribe` | Action | None | Create new prescription |
| `hospital:attach-report` | Navigation | None | Link report to visit |
| `hospital:patient-timeline` | Collection | `collection` | Full patient history |

## Connectedness Mechanism
1. **Resource Navigation**:
   ```json
   {
     "_links": {
       "self": {"href": "/patients/123", "method": "GET"},
       "hospital:visits": {"href": "/visits?patient=123", "method": "GET"}
     }
   }

## Error Recovery
```json
{
  "error": "Invalid dosage",
  "_links": {
    "hospital:corrective-action": {
      "href": "/prescriptions/help",
      "method": "GET"
    }
  }
}
```


---

### **2. Profile Documentation (New File: `profiles/hospital-profile.json`)**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Hospital API Profile",
  "description": "Defines link relations and semantic descriptors",
  "relations": {
    "self": {
      "method": "GET",
      "description": "Canonical resource URI"
    },
    "hospital:prescribe": {
      "method": "POST",
      "schema": {
        "$ref": "schemas/prescription.json"
      }
    }
  },
  "semanticDescriptors": {
    "Diagnosis": {
      "@context": "https://schema.org",
      "@type": "MedicalCondition"
    },
    "Prescription": {
      "@context": "https://schema.org",
      "@type": "DrugPrescription"
    }
  }
}
```

### 3. Testing Suite

### Found Errors
1. **Missing HATEOAS in 404**  
   **Fix**: Added error recovery links to all 4xx/5xx responses  
2. **Broken Pagination Links**  
   **Fix**: Corrected URL generation in `Hateoas` class  

### How to Run Tests
```bash
# Install dependencies
pip install -r test_requirements.txt

# Run all tests
./run_tests.sh

# Sample test case (patient API)
python -m pytest tests/test_patient_api.py -v
```

## Test Data Population

```bash
flask seed-db  # Seeds sample patients/visits
```

### **4. Automated Test Scripts (New File: `run_tests.sh`)**
```bash
#!/bin/bash

# Run functional tests
echo "Running API tests..."
pytest tests/ --cov=app --cov-report=html

# Validate HATEOAS links
echo "Validating hypermedia..."
python -c "
from app.hateoas import validate_links
validate_links()
"

# Check error responses
echo "Testing error cases..."
curl -X GET http://localhost:5000/patients/999 \
  -H 'Accept: application/json' | jq '._links'
```


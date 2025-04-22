# API Documentation

## Interactive Docs
Access Swagger UI at: `http://localhost:5000/api/docs/`

## Key Resources
### `GET /patients/{id}`
**Response**:
```json
{
  "_links": {
    "self": {"href": "/patients/1", "method": "GET"},
    "hospital:visits": {"href": "/visits?patient=1", "method": "GET"}
  },
  "name": "John Doe",
  "age": 45
}
```

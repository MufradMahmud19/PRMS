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

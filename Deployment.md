**Content**:
```markdown
# Deployment Guide

## Requirements
- Python 3.9+
- Redis (for session storage)

## Steps
1. Initialize database:
   ```bash
   flask init-db
   ```
2. Seed test data:
   ```bash
   flask seed-db
   ```
3. Start server:
   ```bash
   gunicorn --bind :5000 run:app
   ```

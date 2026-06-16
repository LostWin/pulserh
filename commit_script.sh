#!/bin/bash

# Commit 6: Fix DAC schemas
git add pulseAIBackend/app/routers/leaves.py pulseAIBackend/app/schemas/document_schemas.py
git commit -m "fix: resolve DAC schema validation on leaves and documents"

# Commit 7: Fix Admin Dashboard
git add pulseAIBackend/app/routers/admin.py pulseAIBackend/alembic/versions/de48f179c060_add_ai_observability_events_table.py
git commit -m "fix: resolve AI Observability missing imports and table migration"

# Commit 8: Fix API Routing
git add pulseAIBackend/app/routers/alerts.py pulseAIBackend/app/routers/audit.py
git commit -m "fix: resolve API trailing slashes causing CORS on alerts and audit"

# Commit 9: Fix Lazy Loading
git add pulseAIBackend/app/routers/dashboard.py pulseAIBackend/app/routers/predictions.py
git commit -m "fix: resolve MissingGreenlet in lazy loaded relationships for dashboard and predictions"

# Commit 1: Data Models & Migrations
git add pulseAIBackend/alembic/versions/ pulseAIBackend/data_imports/ pulseAIBackend/scripts/
git commit -m "feat: enrich HR data models, migrations, and seed scripts"

# Commit 2: Data Access Control
git add pulseAIBackend/app/schemas/data_access.py pulseAIBackend/app/services/field_access_service.py pulseAIBackend/app/services/document_access_service.py pulseAIFront/src/pages/admin/DataAccess.jsx pulseAIFront/src/lib/dataAccessApi.js pulseAIFront/src/components/ui/FieldVisibilityBadge.jsx
git commit -m "feat: implement Data Access Control (DAC) and field-level visibility"

# Commit 3: Alerts & Websockets
git add pulseAIBackend/app/services/alerting_service.py pulseAIBackend/app/services/websocket_manager.py pulseAIBackend/app/schemas/alert.py pulseAIFront/src/contexts/NotificationContext.jsx pulseAIFront/src/components/NotificationCenter.jsx
git commit -m "feat: implement real-time alerts and websocket notification center"

# Commit 4: HR Analytics & Predictions
git add pulseAIBackend/app/services/hr_analytics_service.py pulseAIBackend/app/services/prediction_* pulseAIBackend/app/routers/talent_insights.py pulseAIBackend/app/schemas/prediction.py pulseAIBackend/app/schemas/talent*.py
git commit -m "feat: add advanced HR analytics and prediction scoring services"

# Commit 5: All remaining backend files
git add pulseAIBackend/app/ pulseAIBackend/tests/ pulseAIBackend/scratch.py pulseAIBackend/pytest.ini pulseAIBackend/requirements.txt pulseAIBackend/test_import.py
git commit -m "feat: add missing backend services, routers, and schemas"

# Commit 10: All remaining frontend files
git add pulseAIFront/src/
git commit -m "feat: add new frontend pages, layouts, and admin dashboards"

# Commit 11: Miscellaneous
git add .
git commit -m "chore: update remaining miscellaneous files and configurations"

echo "Done!"

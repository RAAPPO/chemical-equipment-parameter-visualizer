#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run Django on port 8100
echo "🚀 Starting Django Backend on http://127.0.0.1:8100"
echo "📊 Admin Panel: http://127.0.0.1:8100/admin"
echo "🔌 API Endpoints: http://127.0.0.1:8100/api"
echo ""
python manage.py runserver 8100

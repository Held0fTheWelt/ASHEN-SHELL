# Load environment variables from .env
$env:PLAY_SERVICE_SECRET = "dev-secret-for-local-testing"
$env:PLAY_SERVICE_INTERNAL_API_KEY = "internal-api-key-for-ops"
$env:PLAY_SERVICE_PUBLIC_URL = "http://127.0.0.1:5002"
$env:FLASK_ENV = "test"

# Change to world-engine directory
cd world-engine

# Run world-engine
python -m app.main

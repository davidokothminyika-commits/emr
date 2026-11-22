# Clinical Intelligence Copilot

Demonstration MVP. Synthetic data only.

## Run backend
cd backend
cp ../.env.example .env
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

## Run frontend (dev)
cd frontend
npm install
npm run dev

## Build frontend
cd frontend && npm run build

## Demo credentials
clinician / demo123
admin / admin123

## Notes
- Synthetic data seeded on first startup.
- Active EMR mode: synthetic.
- LLM optional: set LLM_API_KEY in .env.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from .config import APP_NAME
from .database import Base, engine
from .api import auth, patients, laboratory, intelligence, alerts, encounters, followups, referrals, audit, rules, dashboard
from .services.rules_engine import sync_rules, run_rules_for_all

app = FastAPI(title=APP_NAME)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# routers
for r in [auth.router, patients.router, laboratory.router, intelligence.router, alerts.router, encounters.router, followups.router, referrals.router, audit.router, rules.router, dashboard.router]:
    app.include_router(r)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    # seed if empty
    from .seed import seed_if_empty
    seed_if_empty()
    from .database import SessionLocal
    db = SessionLocal()
    try:
        sync_rules(db)
        run_rules_for_all(db)
    finally:
        db.close()

# serve frontend build if exists
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")
    @app.get("/{full_path:path}")
    def spa(full_path: str):
        if full_path.startswith("api"):
            return {"detail": "Not found"}
        index = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index):
            return FileResponse(index)
        return {"detail": "frontend not built"}

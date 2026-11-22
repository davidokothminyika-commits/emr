import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR/'clinical_copilot.db'}")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
SECRET_KEY = os.getenv("SECRET_KEY", "demo-secret-key-change-in-production")
EMR_MODE = os.getenv("EMR_MODE", "synthetic")  # synthetic | openmrs
OPENMRS_BASE_URL = os.getenv("OPENMRS_BASE_URL", "")
OPENMRS_USERNAME = os.getenv("OPENMRS_USERNAME", "")
OPENMRS_PASSWORD = os.getenv("OPENMRS_PASSWORD", "")
RULES_FILE = os.getenv("RULES_FILE", str(BASE_DIR / "rules_config.json"))
APP_NAME = "Clinical Intelligence Copilot"
DEMO_MODE = True

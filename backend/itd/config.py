"""Settings read from environment variables (see .env.example)."""
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")  # "mock" = in-memory (tests only)
# Optional separate database accounts (write authorization): see docs/SECURITY.md
MONGO_URI_ENGINE = os.getenv("MONGO_URI_ENGINE", MONGO_URI)
MONGO_URI_API = os.getenv("MONGO_URI_API", MONGO_URI)
DB_NAME = os.getenv("DB_NAME", "insider_threat")

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_MINUTES = int(os.getenv("JWT_MINUTES", "30"))
REQUIRE_HTTPS = os.getenv("REQUIRE_HTTPS", "0") == "1"      # reject plain-HTTP requests
LOGIN_MAX_FAILURES = int(os.getenv("LOGIN_MAX_FAILURES", "5"))
LOGIN_WINDOW_SECONDS = int(os.getenv("LOGIN_WINDOW_SECONDS", "900"))

# Hosted LLM API (assistant). Without a key the assistant answers from a local template.
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-5-5")
LLM_URL = os.getenv("LLM_URL", "https://api.anthropic.com/v1/messages")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
MAX_QUESTION_CHARS = 300

# Pseudonymize user ids at ingestion (Ethics and Privacy section)
PSEUDONYMIZE = os.getenv("PSEUDONYMIZE", "0") == "1"
PSEUDONYM_KEY = os.getenv("PSEUDONYM_KEY", "change-me-pseudonym-key")

# Session rules (proposal, Preprocessing)
SESSION_MAX_HOURS = 12
AFTER_HOURS_START, AFTER_HOURS_END = 19, 7   # after 19:00 or before 07:00
SPLIT = (0.70, 0.15, 0.15)                   # time-ordered train / validation / test
RANDOM_STATE = 42

from pathlib import Path
from dotenv import load_dotenv
import os

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / '.env')

# Neo4j
NEO_HOST = os.getenv("NEO_HOST", "10.0.0.239")
NEO_PORT = os.getenv("NEO_PORT", 30087)
NEO_USER = os.getenv("NEO_USER", "neo4j")
NEO_PASS = os.getenv("NEO_PASS", "password")
NEO_URI = f'neo4j://{NEO_HOST}:{NEO_PORT}'
NEO_AUTH = (NEO_USER, NEO_PASS)

# spaCy
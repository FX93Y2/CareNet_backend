import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
ARCGIS_API_KEY = os.getenv("ARCGIS_API_KEY")
ARCGIS_PORTAL_URL = os.getenv("ARCGIS_PORTAL_URL")
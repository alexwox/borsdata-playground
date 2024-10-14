import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BORSDATA_API_KEY")
BASE_URL = "https://apiservice.borsdata.se/v1"

if not API_KEY:
    raise ValueError("API key is required. Set BORSDATA_API_KEY in your .env file.")

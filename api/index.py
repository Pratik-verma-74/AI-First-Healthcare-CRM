import os
import sys

# Ensure backend folder is in sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.main import app

# Expose FastAPI app for Vercel Serverless Function
app = app

"""Serve the existing Streamlit interface and FastAPI routes on one Cloud port."""

import os
import sys
from pathlib import Path

import streamlit as st
from starlette.routing import Mount

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.main import app as api

port = st.get_option("server.port")
os.environ.setdefault("API_URL", f"http://127.0.0.1:{port}/api")
app = st.App("app.py", routes=[Mount("/api", app=api)])

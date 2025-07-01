import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import google.generativeai as genai

# 🔐 Set your API key from Streamlit secrets
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# 🧠 Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-pro")

# 🔐 Load GCP service account credentials from secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# ✅ Set up BigQuery client with region
bq_client = bigquery.Client(
    credentials=credentials,
    project=credentials.project_id,
    location="us-east1"  # Adjust if your dataset is in another location
)

# 🎨 Streamlit UI setup
st.set_page_config(page_title="GenAI BigQuery App", layout="centered")
st.t

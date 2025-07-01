import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import google.generativeai as genai
import pandas as pd

# 🔐 API Key from Streamlit Secrets
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# 🔐 Service Account for BigQuery
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)

# ✅ BigQuery Client
bq_client = bigquery.Client(
    credentials=credentials,
    project=credentials.project_id,
    location="us-east1"
)

# 🎨 Streamlit UI
st.set_page_config(page_title="GenAI BigQuery App", layout="centered")
st.title("🔍 Ask BigQuery with Natural Language")
st.markdown("Enter a natural language question and click **Run Query** to see results from BigQuery.")

# 🧼 Initialize session state
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# 🧾 Input + Buttons
col1, col2 = st.columns([4, 1])
with col1:
    user_text = st.text_input("💬 Your question:", value=st.session_state.user_input, key="input_box", placeholder="e.g., show first 5 rows of salesorder")

with col2:
    if st.button("🧹 Clear"):
        st.session_state.user_input = ""
        st.rerun()

# ▶️ Run the query
if st.button("▶️ Run Query") and user_text:
    st.session_state.user_input = user_text  # Save to session
    try:
        with st.spinner("⏳ Generating SQL and querying BigQuery..."):
            # 🧠 Prompt Gemini
            prompt = f"""You are a data expert. Convert the following request to BigQuery Standard SQL:
{user_text}
Assume the table name is `southern-coda-463018-j8.mydataset1.salesorder`."""
            response = genai.GenerativeModel("gemini-1.5-pro").generate_content(prompt)
            raw_text = response.text.strip()

            # ✂️ Extract SQL from markdown/code block
            if "```sql" in raw_text:
                sql = raw_text.split("```sql")[1].split("```")[0].strip()
            else:
                sql = raw_text.split("\n\n")[0].strip()

            # 💬 Show SQL
            st.subheader("Generated SQL:")
            st.code(sql, language="sql")

            # 🔎 Query BigQuery
            query_job = bq_client.query(sql)
            df = query_job.to_dataframe()

            st.subheader("Query Results:")
            st.dataframe(df)

            # 📊 Optional bar chart
            if df.shape[1] == 2 and pd.api.types.is_numeric_dtype(df.iloc[:, 1]):
                st.subheader("📊 Auto Bar Chart:")
                st.bar_chart(df.set_index(df.columns[0]))

    except Exception as e:
        st.error(f"❌ Error: {e}")

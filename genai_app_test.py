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
    location="us-east1"
)

# 🎨 Streamlit UI setup
st.set_page_config(page_title="GenAI BigQuery App", layout="centered")
st.title("🔍 Ask BigQuery with Natural Language")

st.markdown("Enter a natural language question and click **Run Query** to see results from BigQuery.")

# 💬 User input
user_input = st.text_input("💬 Your question:", placeholder="e.g., show first 5 rows of salesorder")

# ▶️ Run the query
if st.button("▶️ Run Query") and user_input:
    try:
        with st.spinner("⏳ Generating SQL and querying BigQuery..."):
            # Prompt Gemini to generate SQL
            prompt = f"""You are a data expert. Convert the following request to BigQuery Standard SQL:
            {user_input}
            Assume the table name is `southern-coda-463018-j8.mydataset1.salesorder`."""
            response = model.generate_content(prompt)

            # 🧹 Clean up Gemini output
            sql = response.text.strip()
            if sql.startswith("```sql"):
                sql = sql.replace("```sql", "").replace("```", "").strip()

            st.subheader("Generated SQL:")
            st.code(sql, language="sql")

            # 🔎 Query BigQuery
            query_job = bq_client.query(sql)
            result_df = query_job.to_dataframe()

            st.subheader("Query Results:")
            st.dataframe(result_df)

    except Exception as e:
        st.error(f"❌ Error: {e}")

import streamlit as st
import pandas as pd
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/predict")

st.set_page_config(page_title="RUL Predictor", layout="wide")

st.title("RUL Predictor")

domain = st.sidebar.selectbox("Select Domain", ["FD001", "FD002", "FD003", "FD004"])

test_file = st.file_uploader("Upload Data", type=["txt"])
rul_file = st.file_uploader("Upload RUL", type=["txt"])

st.write("---")

if st.button("Run Prediction"):
    if test_file is None or rul_file is None:
        st.error("Please upload both test and RUL files.")
    else:
        with st.spinner("Running prediction..."):
            try:
                files = {
                    "test_file": (test_file.name, test_file.getvalue(), "text/plain"),
                    "rul_file": (rul_file.name, rul_file.getvalue(), "text/plain")
                }
                data = {"domain": domain}

                response = requests.post(API_URL, files=files, data=data, timeout=120)

                if response.status_code != 200:
                    st.error(f"Backend error: {response.text}")
                    st.stop()

                result = response.json()
                predictions = result["predictions"]

                result_df = pd.DataFrame(predictions)
                result_df = result_df.rename(columns={
                    "unit": "Unit",
                    "true_rul": "True RUL",
                    "predicted_rul": "Predicted RUL",
                    "alert": "Alert"
                })

                st.success("Prediction completed!")
                st.subheader("Alerts Table")
                st.dataframe(result_df, use_container_width=True)

                critical_df = result_df[result_df["Alert"] == "CRITICAL"]

                if not critical_df.empty:
                    st.error("⚠️ Critical Engines Detected!")
                    st.dataframe(critical_df, use_container_width=True)
                else:
                    st.success("No critical engines detected.")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the backend. Make sure FastAPI is running.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
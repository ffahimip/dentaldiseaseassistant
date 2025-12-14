import streamlit as st
import requests

st.title("Dental Disease Assistant")

audience = st.radio("Audience", ["clinician", "patient"])
findings_json = st.text_area("findings_json")
question = st.text_input("Your question")

DIFY_URL = st.secrets["DIFY_URL"]
DIFY_API_KEY = st.secrets["DIFY_API_KEY"]

if st.button("Ask"):
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": {
            "query": question,
            "Role": audience,
            "findings_json": findings_json
        },
        "response_mode": "blocking",
        "user": "streamlit-user"
    }
    r = requests.post(DIFY_URL, headers=headers, json=payload, timeout=90)
    st.json(r.json())

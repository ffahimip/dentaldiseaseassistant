import requests
import streamlit as st

DIFY_URL = st.secrets["DIFY_URL"]
DIFY_API_KEY = st.secrets["DIFY_API_KEY"]

def call_dify_workflow(user_question: str, audience: str, findings_json: str):
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": {
            "query": user_question,
            "Role": audience,
            "findings_json": findings_json
        },
        "response_mode": "blocking",
        "user": "streamlit-user"
    }
    return requests.post(DIFY_URL, headers=headers, json=payload, timeout=90)

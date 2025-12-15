import streamlit as st
import requests
import json
import os

# -----------------------------
# PAGE SETTINGS
# -----------------------------
st.set_page_config(
    page_title="Dental Disease Assistant (DDA)",
    layout="centered"
)

st.title("🦷 Dental Disease Assistant (DDA)")
st.caption(
    "A retrieval-augmented clinical decision support prototype grounded in AAP, AAE, and ADA guidelines."
)

with st.expander("ℹ️ About this prototype"):
    st.markdown(
        """
        **Dental Disease Assistant (DDA)** is a Retrieval-Augmented Generation (RAG) system.
        It retrieves relevant passages from a curated knowledge base and generates a structured response with references.

        **Safety:** If no supporting evidence is retrieved, the system returns an *Insufficient Evidence* response.
        """
    )

# -----------------------------
# DEBUG: SHOW WHICH SECRETS KEYS ARE VISIBLE (SAFE)
# -----------------------------
with st.expander("🧪 Debug (Secrets) — open only if needed"):
    st.write("Visible secret keys:", list(st.secrets.keys()))
    st.write("Visible env var DIFY_API_KEY:", "YES" if os.environ.get("DIFY_API_KEY") else "NO")

# -----------------------------
# DIFY SETTINGS
# -----------------------------
DIFY_URL = "https://api.dify.ai/v1/chat-messages"

# Robust key loading: Streamlit Secrets OR environment variable fallback
DIFY_API_KEY = st.secrets.get("app-Vg5HnRRHlmhZUlL7T7ud9ofA") or os.environ.get("app-Vg5HnRRHlmhZUlL7T7ud9ofA")

if not DIFY_API_KEY:
    st.error(
        "Missing DIFY_API_KEY in Streamlit Secrets.\n\n"
        "Fix:\n"
        "1) Go to App Settings → Secrets\n"
        "2) Paste ONLY this line (TOML):\n"
        '   DIFY_API_KEY = "app-xxxxxxxxxxxxxxxx"\n'
        "3) Save, wait ~60 seconds, then Reboot app.\n\n"
        f"Debug: Visible secret keys right now: {list(st.secrets.keys())}"
    )
    st.stop()

# -----------------------------
# INPUTS
# -----------------------------
st.subheader("Who is this response for?")
role = st.radio(
    "",
    ["Clinician", "Patient"],
    horizontal=True
)

st.subheader("Clinical Question")
query = st.text_area(
    "Enter your question:",
    placeholder="e.g., What defines periodontitis according to AAP 2018?"
)

st.subheader("Optional Findings (JSON)")
findings_json = st.text_area(
    "If you have structured findings, paste them here (optional):",
    placeholder='{"tooth":"30","finding":"bone loss","severity":"moderate"}'
)

# Optional: validate JSON (does not block submission, just warns)
if findings_json.strip():
    try:
        json.loads(findings_json)
    except json.JSONDecodeError:
        st.warning("Optional Findings is not valid JSON. You can leave it empty or fix formatting.")

# -----------------------------
# RUN BUTTON
# -----------------------------
if st.button("Run Dental Disease Assistant"):
    if not query.strip():
        st.error("Please enter a question before submitting.")
    else:
        with st.spinner("Retrieving guideline-based evidence..."):
            headers = {
                "Authorization": f"Bearer {DIFY_API_KEY}",
                "Content-Type": "application/json"
            }

            # ✅ Correct Dify Chat API payload:
            # - query is TOP-LEVEL
            # - inputs contains only your workflow input variables
            payload = {
                "inputs": {
                    # These must match your Dify Start-node variable names.
                    # If your Start node uses Role (capital R), tell me and we’ll change this key.
                    "role": role,
                    "findings_json": findings_json
                },
                "query": query,
                "response_mode": "blocking",
                "user": "streamlit-user"
            }

            try:
                response = requests.post(
                    DIFY_URL,
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                st.subheader("Assistant Response")

                if response.status_code != 200:
                    st.error(f"Dify API error {response.status_code}")
                    st.code(response.text)
                else:
                    data = response.json()
                    answer = data.get("answer")

                    if answer:
                        st.markdown(answer)
                    else:
                        st.warning("No 'answer' field returned. Showing full JSON:")
                        st.json(data)

            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")

# -----------------------------
# SAFETY DISCLAIMER
# -----------------------------
st.divider()
st.warning(
    "⚠️ **Clinical Disclaimer**\n\n"
    "This tool is for educational decision support only. "
    "It does NOT diagnose, prescribe, or replace the judgment of a licensed dental professional."
)

import streamlit as st
import requests
from uuid import uuid4

st.title("🩺 Healthcare Assistant")
st.write("Enter your symptoms below. The agent will process and recommend an action.")

symptom_input = st.text_input("Symptoms", placeholder="e.g., fever, headache")

if st.button("Submit"):
    if not symptom_input.strip():
        st.warning("Please enter symptoms before submitting.")
    else:
        task_id = str(uuid4())
        payload = {
            "jsonrpc": "2.0",
            "method": "tasks/send",  # ✅ Required by your backend
            "id": "1",
            "params": {
                "task_id": task_id,
                "input": symptom_input,
                "metadata": {
                    "type": "symptom_check"
                }
            }
        }

        try:
            response = requests.post("http://localhost:5000", json=payload)
            result = response.json()

            if "error" in result:
                st.error(f"❌ Agent Error: {result['error']['message']}")
            else:
                st.success("✅ Agent Response:")
                st.json(result["result"])

        except Exception as e:
            st.error(f"Request failed: {e}")

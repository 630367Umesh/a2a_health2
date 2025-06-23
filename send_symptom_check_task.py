import uuid
import requests

task_id = str(uuid.uuid4())

url = "http://localhost:5000"

payload = {
    "jsonrpc": "2.0",
    "method": "tasks/send",
    "id": "1",
    "params": {
        "task_id": task_id,
        "id": task_id,
        "message": {
            "type": "symptom_check",
            "content": "fever, headache"
        },
        "metadata": {
            "source": "test_ui"
        }
    }
}

print(">>\nSending request to:", url)
response = requests.post(url, json=payload)

print("🔵 Status Code:", response.status_code)
print("📨 Response JSON:")
print(response.json())

import asyncio
import httpx
import json

async def send_task():
    url = "http://localhost:10000/tasks/send"  # Corrected endpoint

    payload = {
        "jsonrpc": "2.0",
        "id": "check-symptoms-task-001",
        "method": "tasks/send",
        "params": {
            "id": "check-symptoms-task-001",
            "message": {
                "role": "user",
                "parts": [
                    {"type": "text", "text": "I have a fever, cough, and sore throat."}
                ]
            },
            "input": {
                "symptoms": "fever, cough, sore throat"
            },
            "metadata": {
                "user_id": "user-001"
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)

        print("Status Code:", response.status_code)
        print("Raw Text:", response.text)

        try:
            print("✅ JSON Response:", response.json())
        except Exception as e:
            print("❌ JSON decode failed:", str(e))

if __name__ == "__main__":
    asyncio.run(send_task())

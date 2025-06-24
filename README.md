# 🏥 Healthcare Multi-Agent System (MCP + A2A + LLMs)

This project is a modular healthcare assistant powered by multiple AI agents using Google's SDK, Agent-to-Agent (A2A) communication, and Model Context Protocol (MCP).

---

## 📦 Agents Included

| Agent ID                | Role                                      | Port     |
|-------------------------|-------------------------------------------|----------|
| `host_agent`            | Routes and delegates tasks via A2A        | 10000    |
| `symptom_checker_agent`| Analyzes symptoms and suggests next steps | 10020    |
| `appointment_agent`    | Schedules appointments with specialists   | 10010    |
| `health_records_agent` | Manages patient health records            | 10030    |

---

## 🗂️ Project Structure

health_care/
│
├── agents/
│ ├── host_agent/ # OrchestratorAgent
│ ├── symptom_checker_agent/ # Symptom checking logic
│ ├── appointment_agent/ # Appointment scheduling
│ └── health_records_agent/ # Medical records handler
│
├── client/ # JSON-RPC task sender
│ └── send_symptom_check_task.py
│
├── models/ # Shared Pydantic models
│
├── server/ # A2AServer base class (Starlette)
│
├── ui/ # Optional Streamlit frontend
│
├── llm_config.py # LLM provider configuration
├── agent_registry.json # MCP agent directory
├── requirements.txt # Python dependencies
└── README.md # Project documentation



---

## 🧠 LLM Configuration

Edit `llm_config.py` to configure models per agent:

```python
LLM_CONFIG = {
    "symptom_checker_agent": {
        "model": "llama3-70b-8192",
        "provider": "groq",
        "api_key": "your-groq-api-key"
    },
    "appointment_agent": {
        "model": "gemini-1.5-flash-latest",
        "provider": "google",
        "api_key": "your-gemini-api-key"
    }
}

🌐 Agent Registry (MCP)
Define each agent’s URL and ID in agent_registry.json:

[
  {
    "id": "appointment_agent",
    "url": "http://localhost:10010"
  },
  {
    "id": "symptom_checker_agent",
    "url": "http://localhost:10020"
  },
  {
    "id": "health_records_agent",
    "url": "http://localhost:10030"
  }
]

🚀 Running Agents
Run each agent in a separate terminal window:

# Orchestrator Agent
python agents/host_agent/entry.py

# Symptom Checker Agent
python agents/symptom_checker_agent/__main__.py

# Appointment Agent
python agents/appointment_agent/__main__.py

# Health Records Agent
python agents/health_records_agent/__main__.py




 Test It
Run this command to send a symptom check request:

bash
Copy
Edit
python client/send_symptom_check_task.py
Expected: The request routes through the orchestrator and returns a diagnosis from the symptom_checker_agent.

💻 Optional: Run Streamlit UI
If you’ve implemented the Streamlit UI:

bash
Copy
Edit
streamlit run ui/app.py
🧰 Troubleshooting
Issue	Fix
ImportError: cannot import name 'DiscoveryClient'	Check utilities/a2a/agent_discovery.py contains the right class.
'TaskManager' object has no attribute 'on_send_task'	Make sure on_send_task() exists in your agent’s task manager.
404 Not Found on /tasks/send	Check the server is routing POST requests to / or adjust route.
ValidationError (Pydantic)	Ensure the task has message.parts, id, input, metadata.


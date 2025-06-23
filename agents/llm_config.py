# llm_config.py

import os

def get_llm_config(agent_name: str) -> dict:
    if agent_name == "symptom_checker":
        return {
            "provider": "groq",
            "model": "llama3-70b-8192",
            "api_key": os.getenv("GROQ_API_KEY"),
        }
    elif agent_name == "appointment":
        return {
            "provider": "google",
            "model": "gemini-1.5-flash-latest",
            "api_key": os.getenv("GOOGLE_API_KEY"),
        }
    elif agent_name == "health_records":
        return {
            "provider": "openai",
            "model": "gpt-4o",
            "api_key": os.getenv("OPENAI_API_KEY"),
        }
    else:
        raise ValueError(f"Unknown agent name: {agent_name}")

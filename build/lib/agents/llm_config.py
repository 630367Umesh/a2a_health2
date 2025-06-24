# agents/llm_config.py

import os

def get_llm_config(agent: str):
    if agent == "symptom_checker":
        return {
            "provider": "groq",
            "model": "llama3-70b-8192",
            "api_key": os.getenv("GROQ_API_KEY")
        }
    elif agent == "appointment":
        return {
            "provider": "gemini",
            "model": "gemini-1.5-flash-latest",
            "api_key": os.getenv("GEMINI_API_KEY")
        }
    elif agent == "health_records":
        return {
            "provider": "groq",
            "model": "llama3-8b-8192",
            "api_key": os.getenv("GROQ_API_KEY")
        }
    else:
        raise ValueError(f"Unknown agent type: {agent}")

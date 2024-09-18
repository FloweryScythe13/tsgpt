from types import ModuleType
import math
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import requests
import requests.models
from hamilton.function_modifiers import config

def enforcement_prompt(user_input: str, violation_context: dict) -> str:
    """
    Generates the prompt to be sent to the LLM for determining the appropriate enforcement action.
    """
    with open('src/prompts/enforcement_prompt.txt', 'r') as file:
        prompt_template = file.read()

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["user_input", "radicalization_flag", "dio_name", "dio_category", "dio_sentiment"]
    )

    formatted_prompt = prompt.format(
        user_input=user_input,
        radicalization_flag=violation_context.get("extremism_detected", False),
        dio_name=violation_context.get("entity_name", "None"),
        dio_category=violation_context.get("entity_info", {}).get("Policy Category", "Unknown"),
        dio_sentiment=violation_context.get("aspect_sentiment", "None")
    )

    return formatted_prompt

def get_enforcement_decision(enforcement_prompt: str, mistral_public_url: str) -> dict:
    """
    Sends the enforcement prompt to the Mistral model server and retrieves the enforcement decision.
    """
    input_text = {
        "context": enforcement_prompt,
        "question": "What is the appropriate enforcement action?"
    }
    
    response = requests.post(f'{mistral_public_url}/mistral-inference', json=input_text, stream=False)
    
    return {
        "enforcement_action": response.text.strip(),
        "prompt": enforcement_prompt
    }

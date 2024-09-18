import ast
from hamilton.function_modifiers import extract_fields
from types import ModuleType
import math
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import requests
import requests.models
from knowledge_service.knowledge_retrieval import get_information
import traceback

def detect_entity_support(user_input: str, analyze_affect: dict, ner_public_url: str) -> dict:
    """
    Detect whether the user input text is glorifying or supporting an entity
    from the Dangerous Individuals & Organizations KG.
    """
    input_text = {
        "text": user_input,
        "entity_type": "organization"
    }

    # Function to fetch the response from the Mistral model
    def fetch_ner_entities(input_text):
        response: requests.models.Response = requests.post(f'{ner_public_url}/universal-ner', json=input_text, stream=False)
        response.raise_for_status()
        result = response.json()
        print(result)
        if result.get('ner_output'):
            output = result.get('ner_output').strip()
            try:
                output = ast.literal_eval(output)
            except:
                traceback.print_exc()
                return []
            
            return output
        return []

    def fetch_ner_orgs(user_input):
        input_text = {
            "text": user_input,
            "entity_type": "organization"
        }
        return fetch_ner_entities(input_text)
    
    def fetch_ner_persons(user_input):
        input_text = {
            "text": user_input,
            "entity_type": "person"
        }
        return fetch_ner_entities(input_text)
        
    # Fetch the entities
    extracted_entities = fetch_ner_orgs(user_input)
    extracted_entities.extend(fetch_ner_persons(user_input))
    
    for entity in extracted_entities:
        entity = entity.strip()
        entity_info = get_information(entity, "dangerous_organizations")
        if entity_info:
            analyze_affect.update({
                "entity_detected": True,
                "entity_name": entity,
                "entity_info": entity_info
            })
            return analyze_affect
        entity_info = get_information(entity, 'dangerous_individuals')
        if entity_info:
            analyze_affect.update({
                "entity_detected": True,
                "entity_name": entity,
                "entity_info": entity_info
            })
            return analyze_affect
    analyze_affect['entity_detected'] = False
    return analyze_affect

@extract_fields(
    dict(
        extremism_detected=bool,
        ideology=str,
        type_label=str,
        entity_detected=bool,
        entity_name=str,
        entity_info=dict,
        aspect_sentiment=str
    )
)
def detect_glorification(
    user_input: str,
    detect_entity_support: dict,
    mistral_public_url: str
) -> dict:
    """
    Analyze the sentiment of the input text and determine if it glorifies or supports an entity.
    """
    if detect_entity_support["entity_detected"]:
        with open('src/prompts/detect_glorification.txt', 'r') as file:
            prompt_template = file.read()

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["entity_name", "user_input"]
        )

        formatted_prompt = prompt.format(
            entity_name=detect_entity_support['entity_name'],
            user_input=user_input
        )

        input_text = {
            "context": f"User input text: {user_input}\n\nEntity information: {detect_entity_support['entity_info']}",
            "question": formatted_prompt
        }
        
        response = requests.post(f'{mistral_public_url}/mistral-inference', json=input_text, stream=False)
        
        detect_entity_support.update({
            "aspect_sentiment": response.text.strip()
        })
        return dict(
            **detect_entity_support
        )
    
    detect_entity_support["aspect_sentiment"] = "None"
    return dict(
            **detect_entity_support
        )
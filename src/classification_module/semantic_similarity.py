from statistics import mode
from langchain_community.vectorstores import FAISS
from types import ModuleType
import math
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate
import requests
import requests.models
# from decouple import config


def classify_text(
    user_input: str,
    load_vector_store: ModuleType
) -> dict:
    faiss: FAISS = load_vector_store
    results = faiss.similarity_search_with_relevance_scores(user_input)
    avg_similarity_score = sum([result[1] for result in results]) / len(results)
    if avg_similarity_score > 0.7:
        print(f"Extremism {avg_similarity_score} detected, initiating countermeasures protocol... ")
        print(results)
        label = mode([result[0].metadata.get("label", None) for result in results])
        ideology = mode([result[0].metadata.get("ideology", None) for result in results])
        return {"extremism_detected": True, "ideology": ideology,  "type_label": label}
    else:
        return {"extremism_detected": False, "type_label": None}
    
def analyze_affect(
    user_input: str,
    classify_text: dict,
    mistral_public_url: str
) -> dict:
    if (classify_text["extremism_detected"] == True):
        with open('src/prompts/analyze_affect.txt', 'r') as file:
            prompt_template = file.read()

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["user_input"]
        )

        formatted_prompt = prompt.format(user_input=user_input)

        input_text = {
            "context": f"User input text: {user_input}",
            "question": formatted_prompt
        }
        
        # Function to fetch streaming response
        def fetch_data():
            response: requests.models.Response = requests.post(f'{mistral_public_url}/mistral-inference', json=input_text, stream=False)
            return response.text.strip()

        # Call the function to start fetching data
        result = fetch_data()
        classify_text['sentiment'] = result
        return classify_text
    return classify_text
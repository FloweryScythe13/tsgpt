import gradio as gr
from typing import Annotated

from fastapi import FastAPI, Form, UploadFile
from pydantic import BaseModel
from hamilton import driver
from pandas import DataFrame

from data_module import data_pipeline, embedding_pipeline, vectorstore
from classification_module import semantic_similarity, dio_support_detector
from enforcement_module import policy_enforcement_decider

from decouple import config

app = FastAPI()

config = {"loader": "pd", 
          "embedding_service": "openai", 
          "api_key": config("OPENAI_API_KEY"), 
          "model_name": "text-embedding-ada-002",
          "mistral_public_url": config("MISTRAL_PUBLIC_URL"),
          "ner_public_url": config("NER_PUBLIC_URL")
          }  # or "pd"

dr = (
    driver.Builder()
    .with_config(config)
    .with_modules(data_pipeline, embedding_pipeline, vectorstore, semantic_similarity, dio_support_detector)
    .build()
)

dr_enforcement = (
    driver.Builder()
    .with_config(config)
    .with_modules(policy_enforcement_decider)
    .build()
)

class RadicalizationDetectionRequest(BaseModel):
    user_text: str
    
class PolicyEnforcementRequest(BaseModel):
    user_text: str
    violation_context: dict

class RadicalizationDetectionResponse(BaseModel):
    """Response to the /detect endpoint"""
    values: dict
    
class PolicyEnforcementResponse(BaseModel):
    """Response to the /generate_policy_enforcement endpoint"""
    values: dict
    
@app.post("/detect_radicalization")
def detect_radicalization(
    request: RadicalizationDetectionRequest
) -> RadicalizationDetectionResponse:
    
    results = dr.execute(
        final_vars=["detect_glorification"],
        inputs={"project_root": ".", "user_input": request.user_text}
    )
    print(results)
    print(type(results))
    if isinstance(results, DataFrame):
        results = results.to_dict(orient="dict")
    return RadicalizationDetectionResponse(values=results)

@app.post("/generate_policy_enforcement")
def generate_policy_enforcement(
    request: PolicyEnforcementRequest
) -> PolicyEnforcementResponse:
    results = dr_enforcement.execute(
        final_vars=["get_enforcement_decision"],
        inputs={"project_root": ".", "user_input": request.user_text, "violation_context": request.violation_context}
    )
    print(results)
    print(type(results))
    if isinstance(results, DataFrame):
        results = results.to_dict(orient="dict")
    return PolicyEnforcementResponse(values=results)

# Gradio Interface Functions
def gradio_detect_radicalization(user_text: str):
    request = RadicalizationDetectionRequest(user_text=user_text)
    response = detect_radicalization(request)
    return response.values

def gradio_generate_policy_enforcement(user_text: str, violation_context: str):
    # violation_context needs to be provided in a valid JSON format
    context_dict = eval(violation_context)  # Replace eval with json.loads for safer parsing if it's JSON
    request = PolicyEnforcementRequest(user_text=user_text, violation_context=context_dict)
    response = generate_policy_enforcement(request)
    return response.values

# Define the Gradio interface
iface = gr.Interface(
    fn=gradio_detect_radicalization,  # Function to detect radicalization
    inputs="text",  # Single text input
    outputs="json",  # Return JSON output
    title="Radicalization Detection",
    description="Enter text to detect glorification or radicalization."
)

# Second interface for policy enforcement
iface2 = gr.Interface(
    fn=gradio_generate_policy_enforcement,  # Function to generate policy enforcement
    inputs=["text", "text"],  # Two text inputs, one for user text, one for violation context
    outputs="json",  # Return JSON output
    title="Policy Enforcement Decision",
    description="Enter user text and context to generate a policy enforcement decision."
)

# Combine the interfaces in a Tabbed interface
iface_combined = gr.TabbedInterface([iface, iface2], ["Detect Radicalization", "Policy Enforcement"])

# Start the Gradio interface
iface_combined.launch(server_name="0.0.0.0", server_port=7861)


if __name__ == "__main__":
    import uvicorn
    from threading import Thread

    # Run FastAPI server in a separate thread
    def run_fastapi():
        uvicorn.run(app, host="0.0.0.0", port=8000)
    
    fastapi_thread = Thread(target=run_fastapi)
    fastapi_thread.start()

    # Launch Gradio Interface
    iface_combined.launch()
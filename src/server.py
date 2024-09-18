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



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # specify host and port
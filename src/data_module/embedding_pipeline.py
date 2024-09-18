from types import ModuleType

import numpy as np
import openai
from langchain_community.vectorstores import FAISS 
# from sentence_transformers import SentenceTransformer
from hamilton.function_modifiers import config, extract_fields


@config.when(embedding_service="openai")
@extract_fields(
    dict(
        embedding_dimension=int,
        embedding_metric=str,
    )
)
def embedding_config__openai(model_name: str) -> dict:
    if model_name == "text-embedding-ada-002":
        return dict(embedding_dimension=1536, embedding_metric="cosine")
    # If you support more models, you would add that here
    raise ValueError(f"Invalid `model_name`[{model_name}] for openai was passed.")



@config.when(embedding_service="sentence_transformer")
@extract_fields(
    dict(
        embedding_dimension=int,
        embedding_metric=str
    )
)
def embedding_config__sentence_transformer(model_name: str) -> dict:
    if model_name == "multi-qa-MiniLM-L6-cos-v1":
        return dict(embedding_dimension=384, embedding_metric="cosine")
    # If you support more models, you would add that here
    raise ValueError(f"Invalid `model_name`[{model_name}] for SentenceTransformer was passed.")

@config.when(embedding_service="openai")
def embedding_provider__openai(api_key: str) -> ModuleType:
    """Set OpenAI API key"""
    openai.api_key = api_key
    return openai


@config.when(embedding_service="openai")
def embeddings__openai(
    embedding_provider: ModuleType,
    text_contents: list[str],
    model_name: str = "text-embedding-ada-002",
) -> list[np.ndarray]:
    """Convert text to vector representations (embeddings) using OpenAI Embeddings API
    reference: https://github.com/openai/openai-cookbook/blob/main/examples/Get_embeddings.ipynb
    """
    response = embedding_provider.Embedding.create(input=text_contents, engine=model_name)
    return [np.asarray(obj["embedding"]) for obj in response["data"]]


# @config.when(embedding_service="sentence_transformer")
# def embeddings__sentence_transformer(
#     text_contents: list[str], model_name: str = "multi-qa-MiniLM-L6-cos-v1"
# ) -> list[np.ndarray]:
#     """Convert text to vector representations (embeddings)
#     model card: https://huggingface.co/sentence-transformers/multi-qa-MiniLM-L6-cos-v1
#     reference: https://www.sbert.net/examples/applications/computing-embeddings/README.html
#     """
#     embedding_provider = SentenceTransformer(model_name)
#     embeddings = embedding_provider.encode(text_contents, convert_to_numpy=True)
#     return list(embeddings)

def text_contents2(
    text_contents: list[str]
) -> list[str]:
    return text_contents



def data_objects(
    ids: list[int], ideologies: list[str], labels: list[str], embeddings: list[np.ndarray]
) -> list[tuple]:
    assert len(labels) == len(embeddings) # == len(locations) 
    properties = [dict(id=id, ideology=ideology, label=label) for id, ideology, label in zip(ids, ideologies, labels)]
    embeddings = [x.tolist() for x in embeddings]
    
    return list(zip(labels, embeddings, properties))
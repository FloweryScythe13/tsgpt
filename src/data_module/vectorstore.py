from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from types import ModuleType
import numpy as np

# Note to self: try debugging this by visualizing the current DAG

def client_vector_store(
    api_key: str,
    ids: list[int],
    labels: list[str], 
    text_contents: list[str],
    ideologies: list[str],
    embeddings: list[np.ndarray], 
    # properties: list[dict]
    ) -> ModuleType:
    """Upsert data objects to FAISS index"""
    embedding = OpenAIEmbeddings(openai_api_key=api_key)
    
    properties = [dict(id=id, ideology=ideology, label=label) for id, ideology, label in zip(ids, ideologies, labels)]
    text_embeddings = [x.tolist() for x in embeddings]
    embedding_pairs = list(zip(text_contents, text_embeddings))
    faiss = FAISS.from_embeddings(embedding_pairs, embedding=embedding, metadatas=properties)
    return faiss
    
def save_vector_store(
    client_vector_store: ModuleType
) -> bool:
    client_vector_store.save_local(folder_path=".\data2")
    return True

def load_vector_store(api_key: str) -> ModuleType:
    faiss = FAISS.load_local(folder_path="./data2", embeddings=OpenAIEmbeddings(openai_api_key=api_key), allow_dangerous_deserialization=True)
    return faiss


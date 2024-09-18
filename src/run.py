from __future__ import annotations

from hamilton import base, driver

import logging
import sys
import data_module.data_pipeline  as data_pipeline
import data_module.embedding_pipeline as embedding_pipeline
import data_module.vectorstore as vectorstore
import classification_module.semantic_similarity as semantic_similarity
import classification_module.dio_support_detector as dio_support_detector
import click


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout)

@click.command()
@click.option(
    "--embedding_service",
    type=click.Choice(["openai", "cohere", "sentence_transformer", "marqo"], case_sensitive=False),
    default="sentence_transformer",
    help="Text embedding service.",
)
@click.option(
    "--embedding_service_api_key",
    default=None,
    help="API Key for embedding service. Needed if using OpenAI or Cohere.",
)
@click.option("--model_name", default=None, help="Text embedding model name.")
@click.option("--user_input", help="Content on which to run radicalization detection")
def main(
    embedding_service: str,
    embedding_service_api_key: str | None,
    model_name: str,
    user_input: str
):  
    if model_name is None:
        if embedding_service == "openai":
            model_name = "text-embedding-ada-002"
        elif embedding_service == "cohere":
            model_name = "embed-english-light-v2.0"
        elif embedding_service == "sentence_transformer":
            model_name = "multi-qa-MiniLM-L6-cos-v1"
    
    config = {"loader": "pd", "embedding_service": embedding_service, "api_key": embedding_service_api_key, "model_name": model_name}  # or "pd"
    
    dr = driver.Driver(
        config,
        data_pipeline,
        embedding_pipeline,
        vectorstore,
        semantic_similarity,
        dio_support_detector
    )
    # The `final_vars` requested are functions with side-effects
    print(dr.execute(
        final_vars=["detect_glorification"],
        inputs={"project_root": ".", "user_input": user_input}  # I specify this because of how I run this example.
    ))
    # dr.visualize_execution(final_vars=["save_vector_store"],
    #     inputs={"project_root": ".", "user_input": user_input}, output_file_path='./my-dag.dot', render_kwargs={})

if __name__ == "__main__":
    main()
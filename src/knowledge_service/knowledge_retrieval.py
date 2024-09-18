from langchain.chains import GraphCypherQAChain
import os
# from neo4j_semantic_layer import agent_executor as neo4j_semantic_layer_chain

# add_routes(app, neo4j_semantic_layer_chain, path="\neo4j-semantic-layer")
    

from decouple import config 
from typing import List, Optional, Dict, Type

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain_community.graphs import Neo4jGraph
from neo4j.exceptions import ServiceUnavailable
import re
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

NEO4J_URL = config("NEO4J_URL",)
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = config("NEO4J_PASSWORD")


def remove_lucene_chars(text: str) -> str:
    """Remove Lucene special characters"""
    special_chars = [
        "+",
        "-",
        "&",
        "|",
        "!",
        "(",
        ")",
        "{",
        "}",
        "[",
        "]",
        "^",
        '"',
        "~",
        "*",
        "?",
        ":",
        "\\",
    ]
    for char in special_chars:
        if char in text:
            text = text.replace(char, " ")
    return text.strip()


# TODO: For now (8/24/2024), this search query works for strings written in Latin alphabet, but not
# any other alphabet. Follow-up action item: create a custom Neo4j Lucene analyzer for mixed-language
# data (or find one open-source somewhere), re-index the data, and then add {analyzer: "my_analyzer"}
# to the candidate_query string below. 
def generate_full_text_query(input: str) -> str:
    """
    Generate a full-text search query for a given input string.

    This function constructs a query string suitable for a full-text search.
    It processes the input string by splitting it into words and appending a
    similarity threshold (~0.7) to each word, then combines them using the AND
    operator. Useful for mapping movies and people from user questions
    to database values, and allows for some misspelings.
    """
    full_text_query = ""
    words = [el for el in remove_lucene_chars(input).split() if el]
    for word in words[:-1]:
        full_text_query += f" {word}~0.7 AND"
    full_text_query += f" {words[-1]}~0.7"
    return full_text_query.strip()


candidate_query = """
CALL db.index.fulltext.queryNodes($index, $fulltextQuery, {limit: $limit})
YIELD node
RETURN node.name AS name, 
        node.summary AS summary,
        labels(node) AS label
        
"""

person_description_query = """
MATCH (e:PERSON)-[r:IN_CATEGORY]-(m:CATEGORY)
WHERE e.name = $name
RETURN e.name AS name,
       e.gender AS gender, 
       e.summary AS summary, 
       m.name AS policy_category 
LIMIT 1
"""

organization_description_query = """
MATCH (o:ORGANIZATION)-[r:IN_CATEGORY]-(m:CATEGORY)
WHERE o.name = $name
RETURN o.name AS name, 
       o.summary AS summary, 
       o.description AS description, 
       o.twitterUri AS twitter_uri,
       o.homepageUri AS homepage_uri,
       m.name AS policy_category
LIMIT 1
"""

@retry(
    retry=retry_if_exception_type(ServiceUnavailable),
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=4, max=8)
)
def execute_query(query, params):
    graph = Neo4jGraph(NEO4J_URL, NEO4J_USER, NEO4J_PASSWORD)
    return graph.query(query, params)


def get_candidates(input: str, index: str, limit: int = 3) -> List[Dict[str, str]]:
    """
    Retrieve a list of candidate entities from database based on the input string.

    This function queries the Neo4j database using a full-text search. It takes the
    input string, generates a full-text query, and executes this query against the
    specified index in the database. The function returns a list of candidates
    matching the query, with each candidate being a dictionary containing their name,
    summary, and label (either 'ORGANIZATION' or 'PERSON').
    """
    ft_query = generate_full_text_query(input)
    print(ft_query)
    candidates = execute_query(
        candidate_query, {"fulltextQuery": ft_query, "index": index, "limit": limit}
    )
    return candidates


def get_information(entity: str, index: str) -> dict:
    candidates = get_candidates(entity, index)
    if not candidates:
        return None
    # elif len(candidates) > 1:
    #     newline = "\n"
    #     return (
    #         "Multiple matching people were found. They are not the same person. Need additional information to disambiguate the name. "
    #         "In your <avi_answer> output tag, present the user with the following matched options and ask the user which of the options they meant. "
    #         f"Here are the options: {newline + newline.join(str(d) for d in candidates)}"
    #     )
    candidate = candidates[0]
    description_query = (person_description_query if index == "dangerous_individuals" else organization_description_query)
    
    data = execute_query(
        description_query, params={"name": candidate["name"]}
    )

    if not data:
        return None
    candidate_data = data[0]
    # detailed_info = "\n".join([f"{key.replace('_', ' ').title()}: {value}" for key, value in candidate_data.items()])
    detailed_info = {key.replace('_', ' ').title(): value for key, value in candidate_data.items()}
    return detailed_info
 

class InformationInput(BaseModel):
    entity: str = Field(description="full-text search query of the name of a given entity which are mentioned in the question. Example: 'Alice Bob")
    entity_type: str = Field(
        description="indexed list to search for membership by the entity. Available options are 'dangerous_organizations' and 'dangerous_individuals'"
    )


class DIOInformationTool(BaseTool):
    name = "Dangerous_Individuals_And_Organizations_Information"
    description = (
        "useful for when you need to answer questions about various elected officials or persons running for office. " 
        "Never generate a final answer to the question if multiple candidates were matched by name; in those cases, " 
        "always present the candidate options as a bulleted list and ask for disambiguation in your <avi_answer> tag. Never embellish your descriptions of "
        "the candidate in question or assume their motivations from their professional activities under any circumstances; "
        "remain 100% strictly fact-focused at all times with the outputs of this tool."
    )
    args_schema: Type[BaseModel] = InformationInput

    def _run(
        self,
        entity: str,
        entity_type: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        return get_information(entity, entity_type)

    async def _arun(
        self,
        entity: str,
        entity_type: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        return get_information(entity, entity_type)





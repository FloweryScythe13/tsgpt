import pandas as pd
import numpy as np
import json
import ast


import json
import pandas as pd

# Helper function to parse JSON columns safely
def parse_json(json_str, path):
    try:
        json_obj = json.loads(json_str)
        for p in path:
            json_obj = json_obj[p] if p in json_obj else None
        return json_obj
    except:
        return None

data = pd.read_csv("people-enhanced.csv")

# Apply the parsing function to the necessary columns
data['gender'] = data['gender'].apply(lambda x: parse_json(x, ['normalizedValue']))
data['nationalities'] = data['nationalities'].apply(lambda x: parse_json(x, ['name']))

# Extracting and combining birthPlace attributes
data['birthPlace_city'] = data['birthPlace'].apply(lambda x: parse_json(x, ['city', 'name']))
data['birthPlace_region'] = data['birthPlace'].apply(lambda x: parse_json(x, ['region', 'name']))
data['birthPlace_country'] = data['birthPlace'].apply(lambda x: parse_json(x, ['country', 'name']))

# Other direct and nested attributes
data['languages'] = data['languages'].apply(lambda x: parse_json(x, ['str']))  # assuming this is correct path
data['birthDate'] = data['birthDate'].apply(lambda x: parse_json(x, ['str']))
data['netWorth'] = data['netWorth'].apply(lambda x: parse_json(x, ['value']))

# Extracting location details
data['location_city'] = data['location'].apply(lambda x: parse_json(x, ['city', 'name']))
data['location_region'] = data['location'].apply(lambda x: parse_json(x, ['region', 'name']))
data['location_country'] = data['location'].apply(lambda x: parse_json(x, ['country', 'name']))

# Extracting political affiliations
data['politicalAffiliation'] = data['politicalAffiliation'].apply(lambda x: parse_json(x, ['name']))  # Assuming this is a list

# Selecting required columns for final dataframe
final_columns = [
    'name', 'gender', 'nationalities', 'birthPlace_city', 'birthPlace_region', 'birthPlace_country', 
    'affiliated_with', 'summary', 'languages', 'birthDate', 'netWorth', 'location_city', 'location_region', 
    'location_country', 'politicalAffiliation'
]
final_df = data[final_columns]

final_df.head()

import networkx as nx

# Create a directed graph
G = nx.DiGraph()

# Helper function to safely handle missing or NaN data
def safe_add_edge(graph, from_node, to_node, relationship):
    if pd.notna(from_node) and pd.notna(to_node):
        graph.add_edge(from_node, to_node, relationship=relationship)

# G.clear()  # Clearing the graph to start fresh

for idx, row in final_df.iterrows():
    person_node = row['name']  # Using a generic identifier for simplicity
    
    # Add person node with attributes
    G.add_node(person_node, entity="PERSON", gender=row['gender'], summary=row['summary'],
               languages=row['languages'], birthDate=row['birthDate'], netWorth=row['netWorth'])
    
    if "HATE" not in G:
      G.add_node("HATE", entity="CATEGORY")
    safe_add_edge(G, person_node, "HATE", "IN_CATEGORY")

    # Handling location_city and related locations
    if pd.notna(row['location_city']):
        city_node = row['location_city'] or 'Unknown City'
        G.add_node(city_node, entity="CITY")
        safe_add_edge(G, person_node, city_node, "OPERATES_IN")

        if pd.notna(row['location_region']):
            region_node = row['location_region'] or 'Unknown Region'
            G.add_node(region_node, entity="REGION")
            safe_add_edge(G, city_node, region_node, "LOCATED_IN")

            if pd.notna(row['location_country']):
                country_node = row['location_country'] or 'Unknown Country'
                G.add_node(country_node, entity="COUNTRY")
                safe_add_edge(G, region_node, country_node, "LOCATED_IN")
    # Handling affiliated_with
    if pd.notna(row['affiliated_with']):
      affiliated_node = row['affiliated_with']
      G.add_node(affiliated_node, entity='ORGANIZATION')
      safe_add_edge(G, person_node, affiliated_node, "AFFILIATED_WITH")

    # Handling political affiliations
    if pd.notna(row['politicalAffiliation']):
        affs = row['politicalAffiliation'] if isinstance(row['politicalAffiliation'], list) else [row['politicalAffiliation']]
        for aff in affs:
            aff_node = aff if pd.notna(aff) else 'Unknown Affiliation'
            G.add_node(aff_node, entity="PoliticalAffiliation")
            safe_add_edge(G, person_node, aff_node, "POLITICALLY_AFFILIATED_WITH")

    # Handling nationalities
    if pd.notna(row['nationalities']):
        nat_node = row['nationalities']
        G.add_node(nat_node, entity="NATIONALITY")
        safe_add_edge(G, person_node, nat_node, "HAS_NATIONALITY")

# Summarizing the graph
num_nodes = G.number_of_nodes()
num_edges = G.number_of_edges()
(num_nodes, num_edges, list(G.nodes(data=True))[:5])  # Display first 5 nodes with their attributes

from neo4j import GraphDatabase

# BUG: Need to merge into existing Country and Organization nodes 
# these queries currently produce duplicated nodes

# Define Neo4j connection
host = 'neo4j+s://d6881c31.databases.neo4j.io'
user = 'neo4j'
password = 's3vjqP5cUR81xm-lNeU90qXLHjXy19-OIUfQcOCPhNE'
driver = GraphDatabase.driver(host,auth=(user, password))

print(G.nodes)

def add_graph_to_neo4j(driver, graph):
    with driver.session() as session:
        # Add Nodes
        for node, attrs in graph.nodes(data=True):
          try:
            cypher_query = """
            MERGE (n:{label} {{name: $name}})
            SET n += $props
            """.format(label=(':'.join(attrs['entity']) if isinstance(attrs['entity'], list) else attrs['entity']))  # Dynamically set the label based on the 'entity' attribute
            session.run(cypher_query, name=node, entity=attrs['entity'], props={k: v for k, v in attrs.items() if k not in ['entity']})
          except Exception as ex:
            print(ex)
            print(f"Node: {node}, attrs: {attrs}")

        # Add Edges
        for source, target, attrs in graph.edges(data=True):
            cypher_query = """
            MATCH (a),(b)
            WHERE a.name = $source AND b.name = $target
            MERGE (a)-[r:{relationship}]->(b)
            SET r += $props
            """.format(relationship=attrs['relationship'])  # Dynamically set the relationship type
            session.run(cypher_query, source=source, target=target, props={k: v for k, v in attrs.items() if k not in ['relationship']})

# Finally, call the function to add your graph to Neo4j
add_graph_to_neo4j(driver, G)
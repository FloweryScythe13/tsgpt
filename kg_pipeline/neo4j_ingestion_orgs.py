# After human review of enriched orgs - to make sure we got the right entities back
# Read the file into a dataframe
df = pd.read_csv("dangerous_terror_orgs_enriched_checked.csv", sep='\t', usecols=["name", "Category", "Region", "Type", "Affiliated_With", "Designation_Sources", "isCorrectOrg", "types", "isDissolved", "origin", "description", "homepageUri", "allNames", "revenue", "isNonProfit", "summary", "wikipediaUri", "location", "nbEmployees", "industries", "twitterUri"])
df = df[df['isCorrectOrg'] == 1]
df.head(5)

import ast

def handle_non_string_values(value):
    if not isinstance(value, str):
        return None
    else:
        return value

def safe_loads_json(location_str):
    try:
        return ast.literal_eval(location_str)
    except ValueError as e:
        print(f"Failed to parse location string with ast.literal_eval: {e}")
        return {}

def extract_location_data(location_str):

    if location_str:
        location_dict = safe_loads_json(location_str)
        city = location_dict.get('city', {}).get('name', None)
        region = location_dict.get('region', {}).get('name', None)
        country = location_dict.get('country', {}).get('name', None)
        return city, region, country
    else:
        return None, None, None

def extract_revenue_data(revenue_str):
    if revenue_str:
      revenue_dict = safe_loads_json(revenue_str)
      return revenue_dict.get('value')
    else:
      return None

def extract_industries_data(industries_str):
    if pd.notna(industries_str):
      return safe_loads_json(industries_str)
    else:
      return None


df['location'] = df['location'].apply(handle_non_string_values)
# city, region, country = extract_location_data(row)
df[['city', 'region', 'country']] = df.apply(lambda row: extract_location_data(row['location']), axis=1, result_type='expand')
df['revenue'] = df['revenue'].apply(extract_revenue_data)
df['industries'] = df['industries'].apply(extract_industries_data)
df = df.rename(columns={'name': 'Name'})
print(df[df['industries'].notna()])

import pandas as pd
import networkx as nx
import ast



# Initialize a directed graph
G = nx.DiGraph()

# Adding nodes with the entity type as a node attribute
for index, row in df.iterrows():
    if row['Name'] not in G:
        types = ['ORGANIZATION']
        if not pd.isna(row['Type']) and not pd.isnull(row['Type']):
            # types.extend(ast.literal_eval(row['types']))
            types.append(row['Type'])
        types = [t.replace(' ', '_').upper() for t in types]
        properties = {k: v for k, v in row[["isDissolved", "origin", "description",
                    "homepageUri", "allNames",
                   "revenue", "isNonProfit",
                   "summary", "wikipediaUri",
                   "nbEmployees", "industries", "twitterUri"]].to_dict().items() if pd.notna(row['isDissolved'])}
        G.add_node(row['Name'],
                   entity=types,
                   **properties
                   )

    if row['Category'] not in G:
        G.add_node(row['Category'], entity="CATEGORY")

    # if not pd.isna(row['Type']) and not pd.isnull(row['Type']):
    #     types = [row['Type']]
    #     types.extend(ast.literal_eval(row['types']))
    #     for t in types:
    #         if t not in G:
    #             G.add_node(t, entity='ORGANIZATION_TYPE')

    if pd.notna(row['Region']) and row['Region'] not in G:
        regions = row['Region'].split(',')
        for region in regions:
            G.add_node(region, entity='SUPRAREGION')

    if pd.notna(row['country']) and row['country'] not in G:
        G.add_node(row['country'], entity='COUNTRY')

    if pd.notna(row['region']) and row['region'] not in G:
        G.add_node(row['region'], entity='REGION')

    if pd.notna(row['city']) and row['city'] not in G:
        G.add_node(row['city'], entity='CITY')

    if row['industries']:
        for ind in row['industries']:
            if ind not in G:
                G.add_node(ind, entity='INDUSTRY_CATEGORY')

    # Adding edges to denote relationships
    if not G.has_edge(row['Name'], row['Category']):
        G.add_edge(row['Name'], row['Category'], relationship='IN_CATEGORY')

    if regions:
        for region in regions:
            if not G.has_edge(row['Name'], region):
                G.add_edge(row['Name'], region, relationship='LOCATED_IN')

    # if not pd.isna(row['Type']) and not pd.isnull(row['Type']):
    #     if not G.has_edge(row['Name'], row['Type']):
    #         G.add_edge(row['Name'], row['Type'], relationship='INSTANCE_OF')

    if row['Region'] and not G.has_edge(row['Name'], row['Region']):
        G.add_edge(row['Name'], row['Region'], relationship="OPERATES_IN")

    if pd.notna(row['isDissolved']):
      if pd.notna(row['city']) and pd.notna(row['region']):
        if not G.has_edge(row['city'], row['region']):
            G.add_edge(row['city'], row['region'], relationship="LOCATED_IN")

        if pd.notna(row[['region', 'country']].all()) and not G.has_edge(row['region'], row['country']):
            G.add_edge(row['region'], row['country'], relationship="LOCATED_IN")

        if pd.notna(row['city']) and not G.has_edge(row['Name'], row['city']):
            G.add_edge(row['Name'], row['city'], relationship="LOCATION_BASED_IN")

      if row['industries']:
          for ind in row['industries']:
              if not G.has_edge(row['Name'], ind):
                  G.add_edge(row['Name'], ind, relationship="IN_INDUSTRY")

from neo4j import GraphDatabase

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
            MERGE (n:{label} {{name: $name, entity: $entity}})
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
import pandas as pd

import pandas as pd
import requests
import json

# Load data from the Excel file
df = pd.read_excel(
    "Dangerous Individuals & Organizations.xlsx", 
    sheet_name="Hate - Organizations", 
    header=0, 
    dtype={'Name': 'str', 'Category': 'str', 'Type': 'str', 'Region': 'str'}
)

# Fill missing values
df['Type'].fillna('', inplace=True)
df['Region'].fillna('', inplace=True)

# Print the first 5 rows of the dataframe
print(df.head(5))


# Bulk Enhance with Diffbot
diffbot_token = "ff89145a149ef67d115fac24047b3c32"
diffbot_enhance_url = f"https://kg.diffbot.com/kg/v3/enhance/bulk?token={diffbot_token}"

# Prepare data for bulk enhance operation
orgs = []
for index, row in df.iloc[0:116].iterrows():
    try:
        regions = row['Region'].split(', ')
        primary_region = regions[1] if len(regions) > 1 and (regions[0] == "Global" or regions[0] == 'Western Balkans') else regions[0]
        orgs.append({"type": "Organization", "name": row['Name'], "location": primary_region})
    except Exception as ex:
        print(row)
        raise ex

# Send data to Diffbot Bulk Enhance API
diffbot_token = "ff89145a149ef67d115fac24047b3c32"
diffbot_enhance_url = f"https://kg.diffbot.com/kg/v3/enhance/bulk?token={diffbot_token}"
payload = json.dumps(orgs)
headers = {'Content-Type': 'application/json'}
response = requests.post(diffbot_enhance_url, headers=headers, data=payload)
job_id = json.loads(response.text)

print(f"Received job ID {job_id} from Diffbot Bulk Enhance API")

# Retrieve enhanced data
url = f"https://kg.diffbot.com/kg/v3/enhance/bulk/{job_id}?token={diffbot_token}"
headers = {'Accept': 'application/json'}
response = requests.get(url, headers=headers)
payload = {
  'format': 'csv',
  'exportspec': 'name;isDissolved;origin;description;homepageUri;allNames;revenue;isNonProfit;summary;wikipediaUri;types;location;fullName;nbEmployees;descriptors;industries;twitterUri', # Return name and homepageUri
  'exportfile': 'org-enhanced.csv'
}
response = requests.get(url, headers=headers, data=payload)

print(response.text)

import pandas as pd
import json
import numpy as np

# Extract the 'entity' object from each row of JSON in response.text
entities = []
for row in response.text.splitlines():
    data = json.loads(row)
    if 'data' in data and data['data']:
        entities.append(data['data'][0]['entity'])
    else:
        entities.append({})

# Create a dataframe from the extracted entities
df_entities = pd.DataFrame(entities)

# Concatenate the dataframe of entities onto df
df = pd.concat([df, df_entities], axis=1)

# Print the concatenated dataframe
print(df)

df.to_csv('dangerous_organizations_enriched.csv', sep='\t')

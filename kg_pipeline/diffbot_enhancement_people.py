import pandas as pd

import json
import requests
import utils
import time


diffbot_token = "eac694eb3931a48bbbb445b1961d6036"

def poll_bulkjob_status(job_id: str):
  url = f"https://kg.diffbot.com/kg/v3/enhance/bulk/{job_id}/status?token={diffbot_token}"

  headers = {"accept": "application/json"}

  response = requests.get(url, headers=headers)
  print(response)
  result = response.json()
  return result.get("content", {}).get("status") == "COMPLETE"

df = pd.read_excel(utils.get_resource_path("../data/Dangerous Individuals & Organizations.xlsx"), sheet_name="Hate - Individuals", header=0, dtype={'Name': 'str', 'Category': 'str', 'Affiliated With': 'str', 'To Add': 'bool', 'Diffbot ID': 'str'})

# df['Type'].fillna('', inplace=True)
# df['Region'].fillna('', inplace=True)
df[['Affiliated With']].fillna('', inplace=True)
df.columns = ["Name", "Category", "Affiliated_With", "To_Add", "Diffbot_ID"]
df_to_add = df[df['To_Add'] == True]
df = df_to_add




diffbot_enhance_url = f"https://kg.diffbot.com/kg/v3/enhance/bulk?token={diffbot_token}&useCache=true"

people = []
for index, row in df.iterrows():
  try:
    if pd.notna(row['Diffbot_ID']):
      person = {'type': "Person", 'id': row['Diffbot_ID'], 'customId': f"{index}"}
    else:
      person = {'type': "Person", 'name': row['Name'], 'customId': f"{index}"}
    people.append(person)
  except Exception as ex:
    print(row)
    raise ex


payload = json.dumps(people)
headers = {
  'Content-Type': 'application/json'
}
response = requests.post(diffbot_enhance_url, headers=headers, data=payload)

print(response)
print(response.text)

job_id = json.loads(response.text)['job_id']
print(f"Received job ID {job_id} from Diffbot Bulk Enhance API")

done: bool = False
while not done:
  print(f"Polling for status of bulkjob {job_id}")
  done = poll_bulkjob_status(job_id)
  if not done:
    time.sleep(7)

url = f"https://kg.diffbot.com/kg/v3/enhance/bulk/{job_id}?format=csv&exportspec=gender%3Borigin%3Bdescription%3Beducations%3Bnationalities%3Btype%3BallNames%3Bskills%3BbirthPlace%3Borigins%3Bid%3Bsummary%3Bimage%3Bimages%3BwikipediaUri%3Blanguages%3BallUris%3Bemployments%3BbirthDate%3Bawards%3BnetWorth%3Bname%3BallDescriptions%3Blocations%3Blocation%3BpoliticalAffiliation%3Breligion%3Binterests%3BnameDetail%3Bage%3BlinkedInUri%3BtwitterUri%3ByoutubeUri%3BinstagramUri%3BfacebookUri%3BnbFollowers%3BgithubUri%3BangellistUri%3BhomepageUri%3BblogUri%3BemailAddresses%3Barticles%3BdeathPlace%3BdeathDate%3Bunions%3BphoneNumbers%3Bcolleagues%3Bfriends%3Bsiblings&exportquery=false&wait=120&token=eac694eb3931a48bbbb445b1961d6036"

headers = {
  'Accept': 'application/json'
}

response = requests.get(url, headers=headers)

print(response.text)

with open(utils.get_resource_path("../data2/people-enhanced.csv"), "w", encoding="utf-8") as f:
  f.write(response.text)


# Extract the 'entity' object from each row of JSON in response.text
# entities = []
# for row in response.text.splitlines():
#     data = json.loads(row)
#     if 'data' in data and data['data']:
#         entities.append(data['data'][0]['entity'])
#     else:
#         entities.append({})

# # Create a dataframe from the extracted entities
# df_individuals = pd.DataFrame(entities)

# # Concatenate the dataframe of entities onto df
# df = pd.concat([df, df_individuals], axis=1)

# # Print the concatenated dataframe
# print(df)

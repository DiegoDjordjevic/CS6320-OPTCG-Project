import chromadb
from pprint import pprint
import json

client = chromadb.Client()

card_base = client.create_collection("OPTCG")

f = open("asia-cardlist.json")
data = json.load(f)
documents = []
ids = []
for i in data:
    documents.append(i)
    ids.append(data[i]['card_id'])
print(ids)

card_base.upsert(documents=documents, ids=ids)

results = card_base.query(
    query_texts=["Red Pirate"], # Chroma will embed this for you
    n_results=2 # how many results to return
)

print(results)
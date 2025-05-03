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
    documents.append(str(data[i]))
    ids.append(data[i]['card_id'])
#print("documents" + str(documents))

card_base.upsert(documents=documents, ids=ids)
results = card_base.query(
    query_texts=["Strawhat, Red, Leader"], # Chroma will embed this for you
    n_results=5 # how many results to return
)

print(results)
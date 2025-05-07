import json
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))

vector_store = Chroma(
    collection_name="OPTCGCards",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db_texts",
)

f = open("asia-cardlist.json")
data = json.load(f)
documents = []
ids = []
metadata = []
for i in data:
    documents.append(str(data[i]))
    metadata.append({"card_type": data[i]['card_type']})
    ids.append(data[i]['card_id'])
vector_store.add_texts(texts=documents, ids=ids, metadatas=metadata)


retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 5, "fetch_k": 25}, filter={"card_type": "LEADER"})
retriever.invoke("Strawhat, Red, Leader")

results = vector_store.similarity_search(query="Strawhat, Red, Leader",k=5,filter={"card_type": "LEADER"})
for doc in results:
    print(f"* {doc.page_content} [{doc.metadata}]")
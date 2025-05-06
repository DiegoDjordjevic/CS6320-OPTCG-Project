import chromadb
import json
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv
from langchain_core.documents import Document


load_dotenv()
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))

vector_store = Chroma(
    collection_name="OPTCG",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",
)

f = open("asia-cardlist.json")
data = json.load(f)
documents = []
ids = []
for i in data:
    documents.append(Document(page_content=str(data[i]), metadata={"card_type": data[i]['card_type']}))
    ids.append(data[i]['card_id'])
#print("documents" + str(documents))
vector_store.add_documents(documents=documents, ids=ids)


retriever = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 5, "fetch_k": 25}, filter={"card_type": "LEADER"})
retriever.invoke("Strawhat, Red, Leader")

results = vector_store.similarity_search(query="Strawhat, Red, Leader",k=5,filter={"card_type": "LEADER"})
for doc in results:
    print(f"* {doc.page_content} [{doc.metadata}]")
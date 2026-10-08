#This is a one time script to populate the company policies database

import os
import chromadb
from src.retrieval import chunk_text
from src.retrieval import embed
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')



client = chromadb.PersistentClient(path="./chroma_db")

# If company_policies exists then delete it
try:
    client.delete_collection(name="company_policies")
except Exception:
    pass

collection = client.get_or_create_collection(name="company_policies")

DATA_DIR = os.path.abspath("data/policies")
files = os.listdir(DATA_DIR)

ids = []
documents = []
metadatas = []
embeds = []
count = 1
    
for file in files:
    #Read each file in folder and call chunk_text from retrieval.py for each
    f = open(os.path.join(DATA_DIR,file))
    text = f.read()
    #chunk_text(text, word count , overlap)
    chunk = chunk_text(text, 32 , 8)

    FILE_PATH = os.path.join(DATA_DIR, file)
    stats = os.stat(FILE_PATH)
    
    #loop through each chunk an array and store them in documents with corresponding id
    for chunks in chunk:
        ids.append("id" + str(count))
        documents.append(chunks)

        #call embed from retrieval.py to generate vectors for each chunk
        embeds.append(embed(chunks, model))

        #savae metadata for each chunk
        metadatas.append({
            "filename": os.path.basename(FILE_PATH),
            "size_bytes": stats.st_size
            } )

        count += 1
           

f.close()
collection.add(ids = ids ,embeddings = embeds, documents = documents, metadatas = metadatas)

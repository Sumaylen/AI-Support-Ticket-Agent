import chromadb
import math
import os

db_path = os.path.abspath("chroma_db")
client = chromadb.PersistentClient(path=db_path)
collection = client.get_or_create_collection(name="company_policies")

#splits up text strings into chunks of words based on chunk size including some overlap to preserve context
def chunk_text(text, chunk_size, overlap):
    # Error Handling
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")
    
    chunks = text.split()
    chunksSelected = []
    start = 0
        
    while start < len(chunks):
        end = start + chunk_size
        #IF only a few words remain, read to the end to avoid small chunks
        if (len(chunks[start:end])) < chunk_size:
            chunksSelected.append(" ".join(chunks[start:]))
            break
       
        chunksSelected.append(" ".join(chunks[start:end]))
        start = (start + chunk_size) - overlap


    return chunksSelected
    

#Create embed vectors to store in chromaDB
def embed(texts, model):
    vectors = model.encode(texts)
    return vectors.tolist()

#Retrieve function returns the k most relevant chunks for a given question.
def retrieve(question, k):
    results = collection.query(
        query_texts=[question],
        n_results=k
    )

    #only care about the first entry in the query list
    docs = results["documents"][0]
    metas = results["metadatas"][0]

    combined = []

    #loop through each each relevant chunk and add the chunk text and corresponding file name to an array
    for i in range(len(docs)):
        entry = {
            "text": docs[i],
            "source": metas[i]["filename"]
        }
        combined.append(entry)

    print(combined)
    return combined

retrieve("How are international orders handled?", 3)

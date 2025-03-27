import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import csv
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Global lists to store original questions and combined texts
questions = []
combined_texts = []
embeddings_list = []

def combine_fields(row):
    # Combine question, keywords, and answer into a single string
    question = row.get("question", "").strip()
    keywords = row.get("keywords", "").strip()
    answer = row.get("answer", "").strip()
    return f"{question} | Keywords: {keywords} | Answer: {answer}"

# Load data from CSV file and generate embeddings for each record
with open("qa_keyword.csv", newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        q = row["question"].strip()
        questions.append(q)
        
        combined = combine_fields(row)
        combined_texts.append(combined)
        
        emb = model.encode(combined)
        embeddings_list.append(emb)

# Convert embeddings to a NumPy array of type float32 and build FAISS index
embeddings = np.array(embeddings_list, dtype='float32')
d = embeddings.shape[1]
index = faiss.IndexFlatL2(d)
index.add(embeddings)

def generate_final_answer(user_query, retrieved_context):
    # Combine the query and retrieved context into a prompt
    prompt = (
        f"User Query: {user_query}\n\n"
        f"Relevant Information:\n{retrieved_context}\n\n"
        "Generate a comprehensive and well-structured answer."
    )
    
    headers = {
        "Authorization": f"Bearer {deepseek_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 250
    }
    
    response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data)
    response.raise_for_status()  # Raise an error if the request failed
    
    # Log the raw response for debugging
    resp_json = response.json()
    print("DeepSeek API Response:", resp_json)
    
    # Try to extract the generated text.
    if "choices" in resp_json:
        # Assuming response structure similar to OpenAI Chat API:
        final_text = resp_json["choices"][0]["message"]["content"]
    elif "result" in resp_json:
        final_text = resp_json["result"]
    else:
        final_text = "No text generated."
        
    return final_text

@app.get("/generate")
def generate(q: str = Query(..., description="Query string to search for relevant information")):
    # Generate embedding for the incoming query
    query_emb = model.encode([q])
    query_emb = np.array(query_emb, dtype='float32')
    
    # Retrieve top k records from FAISS index
    k = 3
    distances, indices = index.search(query_emb, k)
    
    # Concatenate the retrieved combined texts to form the context
    retrieved_context = "\n\n".join([combined_texts[i] for i in indices[0]])
    
    # Generate final answer using DeepSeek API
    final_answer = generate_final_answer(q, retrieved_context)
    
    # Return only the final answer
    return {"final_answer": final_answer}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
    
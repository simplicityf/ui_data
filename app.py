from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uidata
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data stored in-memory (or you can use a database)
qa_data = uidata.qa_data

@app.get("/search")
def search_question(q: str):
    for item in qa_data:
        if q.lower() in item["question"].lower():
            return {"question": item["question"], "answer": item["answer"]}
    return {"error": "No matching answer found"}


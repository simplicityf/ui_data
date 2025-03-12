from fastapi import FastAPI
from typing import Dict, List
import uidata
app = FastAPI()

# Data stored in-memory (or you can use a database)
qa_data = uidata.qa_data

@app.get("/search")
def search_question(q: str):
    for item in qa_data:
        if q.lower() in item["question"].lower():
            return {"question": item["question"], "answer": item["answer"]}
    return {"error": "No matching answer found"}


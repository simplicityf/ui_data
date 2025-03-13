from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from difflib import SequenceMatcher
import keyword_1

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load keyword-based data
qa_data = keyword_1.qa_keyword
def format_answer(answer, depth=0):
    """
    Recursively formats nested dictionaries and lists into readable strings.
    """
    indent = "  " * depth  # Indentation for readability
    formatted_answer = ""

    if isinstance(answer, dict):
        for key, value in answer.items():
            formatted_answer += f"{indent}**{key}**:\n{format_answer(value, depth + 1)}\n"
    elif isinstance(answer, list):
        formatted_answer += "\n".join(f"{indent}- {format_answer(item, depth + 1)}" for item in answer)
    else:
        formatted_answer += f"{indent}{answer}"
    
    return formatted_answer.strip()

def search_best_match(user_query):
    """Find the best matching question based on keyword overlap and similarity."""
    query_keywords = set(user_query.lower().split())
    best_match = None
    best_score = 0

    for item in qa_data:
        question_keywords = set(item["keywords"])
        common_keywords = query_keywords.intersection(question_keywords)
        similarity = SequenceMatcher(None, user_query.lower(), item["question"].lower()).ratio()
        score = len(common_keywords) + similarity  # Combine keyword match and string similarity

        if score > best_score:
            best_score = score
            best_match = item
    
    return best_match

@app.get("/search")
def search_question(q: str):
    match = search_best_match(q)
    if match:
        formatted_response = format_answer(match["answer"])
        return {"question": match["question"], "answer": formatted_response}
    
    return {"error": "No matching answer found"}

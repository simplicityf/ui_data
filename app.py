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

# Load data from uidata
qa_data = uidata.qa_data

def format_answer(answer, depth=0):
    """
    Recursively formats nested dictionaries and lists into readable strings.
    - Handles dictionaries, lists, and plain text.
    - Uses indentation for better readability.
    """
    indent = "  " * depth  # Creates indentation for nested data
    formatted_answer = ""

    if isinstance(answer, dict):
        for key, value in answer.items():
            formatted_answer += f"{indent}**{key}**:\n{format_answer(value, depth + 1)}\n"
    
    elif isinstance(answer, list):
        formatted_answer += "\n".join(f"{indent}- {format_answer(item, depth + 1)}" for item in answer)
    
    else:  # If it's just a string or number, return as is
        formatted_answer += f"{indent}{answer}"
    
    return formatted_answer.strip()

@app.get("/search")
def search_question(q: str):
    for item in qa_data:
        if q.lower() in item["question"].lower():
            formatted_response = format_answer(item["answer"])
            return {"question": item["question"], "answer": formatted_response}
    
    return {"error": "No matching answer found"}

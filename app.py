from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from difflib import SequenceMatcher
import keyword_1  # This file contains qa_keyword

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the keyword-based data from your file
qa_data = keyword_1.qa_keyword

def present_answer_plain(answer):
    """
    Converts an answer (which can be a list or dict) to a plain text string
    that contains only its values (without any keys, braces, or brackets).
    """
    if isinstance(answer, list):
        parts = []
        for a in answer:
            if isinstance(a, dict):
                inner_parts = []
                for v in a.values():
                    if isinstance(v, list):
                        inner_parts.append(", ".join(str(x) for x in v))
                    else:
                        inner_parts.append(str(v))
                parts.append("\n".join(inner_parts))
            else:
                parts.append(str(a))
        return "\n".join(parts)
    elif isinstance(answer, dict):
        inner_parts = []
        for v in answer.values():
            if isinstance(v, list):
                inner_parts.append(", ".join(str(x) for x in v))
            else:
                inner_parts.append(str(v))
        return "\n".join(inner_parts)
    else:
        return str(answer)

def search_all_matches(user_query):
    """
    Searches qa_data for entries where at least one keyword phrase appears in the user query.
    Each match is scored based on the count of keyword matches (weighted) plus a similarity ratio.
    """
    query_lower = user_query.lower()
    matches = []
    for item in qa_data:
        keyword_match_count = sum(1 for kw in item["keywords"] if kw.lower() in query_lower)
        if keyword_match_count > 0:
            similarity = SequenceMatcher(None, query_lower, item["question"].lower()).ratio()
            score = keyword_match_count * 2 + similarity
            matches.append((item, score))
    matches.sort(key=lambda x: x[1], reverse=True)
    return [match[0] for match in matches]

def present_match_plain(match):
    """
    Returns a plain text string that includes the question (first line)
    and the answer (next line(s)) without any keys.
    """
    question_text = match["question"].strip()
    answer_text = present_answer_plain(match["answer"]).strip()
    return f"{question_text}\n{answer_text}"

@app.get("/search", response_class=PlainTextResponse)
def search_question(q: str):
    matches = search_all_matches(q)
    if matches:
        # Join all match outputs with two newlines between each block.
        result = "\n\n".join(present_match_plain(m) for m in matches)
        return result
    return ""

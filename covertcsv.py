import csv
import json
import keyword_1

# Your data (partial snippet shown; include the full qa_keyword list from your file)
qa_keyword = keyword_1.qa_keyword

def clean_text(text):
    # Remove extra spaces and newlines
    return " ".join(text.split())

def list_to_str(lst):
    # Convert a list to a semicolon-separated string, cleaning each element
    return "; ".join(clean_text(item) for item in lst)

def process_answer(answer):
    # The answer field can be a list or a dict; handle accordingly.
    if isinstance(answer, list):
        # For lists, join items with a separator.
        return " | ".join(clean_text(str(item)) for item in answer)
    elif isinstance(answer, dict):
        # Convert dictionaries to JSON strings (you can customize formatting if needed)
        return json.dumps(answer, ensure_ascii=False)
    else:
        return clean_text(str(answer))

# Specify the CSV file name
csv_file = "qa_keyword.csv"

# Write data to CSV
with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    # Write header row
    writer.writerow(["question", "keywords", "answer"])
    
    # Process each record
    for record in qa_keyword:
        question = clean_text(record.get("question", ""))
        keywords = list_to_str(record.get("keywords", []))
        answer = process_answer(record.get("answer", ""))
        writer.writerow([question, keywords, answer])

print(f"CSV file '{csv_file}' has been created successfully.")

from helpers import read_file, extract_data, get_missing_fields, decide_route
import os


def process_claim(file_path):
    text = read_file(file_path)

    if not text.strip():
        return {
            "extractedFields": {},
            "missingFields": [],
            "recommendedRoute": "manual_review",
            "reasoning": "could not read file"
        }

    data = extract_data(text)
    missing = get_missing_fields(data)
    route, reason = decide_route(data, missing)

    return {
        "extractedFields": data,
        "missingFields": missing,
        "recommendedRoute": route,
        "reasoning": reason
    }




def process_folder(folder_path):
    results = []

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        if os.path.isdir(file_path):
            continue

        if not file_name.lower().endswith((".txt", ".pdf")):
            continue

        results.append(process_claim(file_path))

    return results

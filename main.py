import sys
import os
import json
from helpers import read_file, extract_data, get_missing_fields, decide_route


# Process single file
def process(file_path):
    text = read_file(file_path)

    if not text.strip():
        print(f"\nSkipping empty file: {file_path}")
        return

    data = extract_data(text)
    missing = get_missing_fields(data)
    route, reason = decide_route(data, missing)

    print(f"\n--- Processing: {file_path} ---")

    print("\nExtracted Data:")
    print(json.dumps(data, indent=2))

    print("\nMissing Fields:")
    print(missing)

    print("\nRoute:", route)
    print("Reason:", reason)


# Process folder
def process_folder(folder_path):
    for file in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file)

        if os.path.isfile(full_path):
            process(full_path)


# Entry point
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <file_path_or_folder>")
    else:
        path = sys.argv[1]

        if os.path.isdir(path):
            process_folder(path)
        else:
            process(path)
from fnol import process_claim, process_folder
import json
import os

input_path = "sample-claims" 

if __name__ == "__main__":

    if os.path.isdir(input_path):
        result = process_folder(input_path)
    else:
        result = process_claim(input_path)

    print("\n--- FNOL OUTPUT ---\n")
    print(json.dumps(result, indent=2))


# FNOL Claims Processor

A Python-based system to process First Notice of Loss (FNOL) documents by extracting structured data, validating required fields, and routing claims intelligently.

---

## 🚀 Features

* Supports `.txt` and `.pdf` claim documents
* Extracts key fields like policy details, incident info, and asset data
* Cleans and normalizes raw input text
* Identifies missing required fields
* Automatically routes claims based on business rules

---

## 🧠 Approach

### 1. File Handling

The system reads input files and detects whether they are `.txt` or `.pdf`, using appropriate methods to extract text.

### 2. Text Normalization

Raw text is cleaned by removing unnecessary formatting, extra spaces, and irrelevant sections like ACORD blocks.

### 3. Data Extraction

Regex-based patterns are used to extract structured fields such as:

* Policy details
* Incident information
* Claimant and contact details
* Asset details
* Estimated damage

### 4. Data Cleaning

Extracted values are cleaned to remove noise such as emails, long numbers, and irrelevant keywords.

### 5. Claim Classification

The claim type is determined using keyword-based logic:

* Injury → if words like “injured”, “hospital” are present
* Property → default

### 6. Validation

The system checks for required fields:

* policy_number
* location
* date_of_loss
* description
* estimated_damage
* claim_type

### 7. Routing Logic

Claims are routed based on predefined rules:

* Missing fields → Manual Review
* Suspicious keywords → Investigation
* Injury claims → Specialist handling
* Low damage (< 25,000) → Fast Track
* Otherwise → Standard processing

---

## 🛠️ Tech Stack

* Python
* Regex
* PyPDF2

---

## ▶️ Installation

```bash
git clone https://github.com/manjunath-bhat15/fnol-claims-processor.git
cd fnol-claims-processor
pip install -r requirements.txt
```

---

## ▶️ Usage

```bash
python main.py
```

---

## 📦 Example Output

```json
{
  "policy_number": "ABC12345",
  "location": "Bangalore",
  "date_of_loss": "12/03/2026",
  "description": "Vehicle collision at signal causing front damage",
  "estimated_damage": 18000,
  "claim_type": "property"
}
```

---

## 💡 Future Improvements

* Replace regex with NLP-based extraction
* Build REST API using FastAPI
* Add logging and monitoring
* Improve fraud detection using machine learning

---

## 👨‍💻 Author

Manjunath Bhat

import re
import os


# File readers
def read_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        return read_txt(file_path)
    elif ext == ".pdf":
        return read_pdf(file_path)
    return ""


def read_txt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def read_pdf(file_path):
    try:
        import PyPDF2

        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        return text
    except Exception:
        return ""


# Normalize text
def normalize_text(text):
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"ACORD.*?(?=\n\n|\Z)", "", text, flags=re.I | re.S)
    return text.strip()


# Extract first regex match
def extract_first(patterns, text, flags=re.I):
    for p in patterns:
        match = re.search(p, text, flags)
        if match:
            return match.group(1).strip()
    return None


# Clean extracted values
def clean_value(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return value

    value = str(value).strip()
    value = re.sub(r"\S+@\S+", "", value)
    value = re.sub(r"\b\d{10,}\b", "", value)

    junk = ["ACORD", "FORM", "PAGE", "INSURED VEHICLE"]
    if any(j in value.upper() for j in junk):
        return None

    value = " ".join(value.split())
    return value if len(value) >= 3 else None


# Extract description
def extract_description(text):
    patterns = [
        r"Description\s+of\s+(?:Accident|Loss|Incident)[:\s]+(.*?)(?:\n[A-Z][a-z]+\s|$)",
        r"Description[:\s]+(.*?)(?:\n[A-Z][a-z]+\s|$)",
    ]

    content = extract_first(patterns, text, flags=re.I | re.S)
    if not content:
        return None

    for word in ["Claimant", "Contact", "Phone", "Email", "Policy"]:
        parts = re.split(rf"\b{word}\b", content, flags=re.I)
        if len(parts) > 1:
            content = parts[0]

    content = re.sub(r"[^a-zA-Z0-9.,\s]", " ", content)
    content = " ".join(content.split())

    return content if len(content.split()) >= 8 else None


# Extract main data
def extract_data(text):
    text = normalize_text(text)

    data = {}

    # Policy info
    data["policy_number"] = extract_first(
        [r"Policy\s*(?:Number|No)[:\-]?\s*([A-Z0-9\-]+)"], text
    )
    data["policyholder_name"] = extract_first(
        [r"(?:Policyholder|Insured)\s*Name[:\-]?\s*([A-Za-z ]+)"], text
    )
    data["effective_dates"] = extract_first(
        [r"Policy\s+Effective\s+Dates[:\-]?\s*([^\n]+)"], text
    )

    # Incident info
    data["location"] = extract_first([r"Location.*?:\s*([^\n\r]+)"], text)
    data["date_of_loss"] = extract_first(
        [r"Date\s+of\s+(?:Loss|Incident)[:\s]+([\d/.-]+)"], text
    )
    data["time"] = extract_first(
        [r"Time.*?:\s*([\d:]+\s*[APMapm]+)"], text
    )
    data["description"] = extract_description(text)

    # Parties
    data["claimant"] = extract_first(
        [r"Claimant\s*Name[:\-]?\s*([A-Za-z ]+)"], text
    )
    data["contact"] = extract_first(
        [r"Phone[:\-]?\s*(\d{10})"], text
    )
    data["third_parties"] = extract_first(
        [r"Third\s+Parties.*?:\s*(.*?)(?:\n[A-Z]|$)"], text, re.I | re.S
    )

    # Asset info
    data["asset_type"] = extract_first(
        [r"Asset\s+Type[:\-]?\s*([A-Za-z]+)", r"(Vehicle|Car|Bike)"], text
    )
    data["asset_id"] = extract_first(
        [r"(?:VIN|Vehicle\s*ID)[:\-]?\s*([A-Z0-9]+)"], text
    )

    damage = extract_first(
        [r"(?:Estimated?\s*Damage|Estimate).*?([\d,]+)"], text
    )
    data["estimated_damage"] = int(damage.replace(",", "")) if damage else None

    # Attachments
    data["attachments"] = extract_first(
        [r"Attachments?[:\s]+([^\n\r]+)"], text
    )

    # Claim type detection
    desc = (data.get("description") or "").lower()
    if any(w in desc for w in ["injury", "injured", "hospital", "medical"]):
        data["claim_type"] = "injury"
    else:
        data["claim_type"] = "property"

    # Final cleaning
    for k, v in data.items():
        data[k] = clean_value(v)

    return data


# Get missing required fields
def get_missing_fields(data):
    required = [
        "policy_number",
        "location",
        "date_of_loss",
        "description",
        "estimated_damage",
        "claim_type",
    ]
    return [f for f in required if not data.get(f)]


# Decide processing route
def decide_route(data, missing):
    if missing:
        return "manual_review", "missing required fields"

    desc = (data.get("description") or "").lower()

    if any(w in desc for w in ["fraud", "staged", "fake", "inconsistent"]):
        return "investigation", "suspicious keywords detected"

    if data.get("claim_type") == "injury":
        return "specialist", "injury claims need specialist handling"

    damage = data.get("estimated_damage") or 0
    if damage < 25000:
        return "fast_track", "low estimated damage"

    return "standard", "default processing"
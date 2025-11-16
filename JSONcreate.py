import json

from LLMAPIs import get_response
from pydantic import BaseModel

class PatientInfo(BaseModel):
    patient_info: dict
    visit_motivation: str

class Symptoms(BaseModel):
    symptoms: list[str]

class VitalSigns(BaseModel):
    blood_pressure: dict | None
    heart_rate: dict | None
    oxygen_saturation: dict | None
    cholesterol_level: dict | None
    glucose_level: dict | None
    temperature: dict | None
    respiratory_rate: dict | None

def get_json_segment(model, notes):
    visit_motivation = get_response(model,f"""
    You are a strict information extraction system.
    Extract only the explicitly stated or directly implied information.
    Each visit_motivation must be one of the listed options.
    Return ONLY valid JSON (no extra text).

    Schema:
    {{
    "patient_info": {{
        "age": <number>,
        "gender": "Male" | "Female"
    }},
    "visit_motivation": <string>  # single best matching condition from the list below
    }}

    Possible values for "visit_motivation" are:
    ["Anemia", "Allergies", "Diabetes (Type 2)", "Tuberculosis (TB)", "Depression", "Asthma",
    "Hypertension (High Blood Pressure)", "Influenza (Flu)", "Anxiety Disorders", 
    "Gastroesophageal Reflux Disease (GERD)", "Heart Disease (Coronary Artery Disease)", 
    "Pneumonia", "Urinary Tract Infection (UTI)", "Common Cold", "Ear Infection (Otitis Media)",
    "Eczema (Atopic Dermatitis)", "COVID-19", "Strep Throat", "Sinusitis", "Chronic Obstructive Pulmonary Disease (COPD)"]

    ---
    Medical Note:
    {notes}
    """,
    format=PatientInfo)
    
    symptoms = get_response(model,f"""
You are a strict information extraction system.

Extract only the information that is explicitly stated or directly implied in the following medical note. 
If a field or value is not mentioned, omit it completely from the JSON output. 
Do NOT infer, guess, or add information that is not in the note.

Return ONLY valid JSON (no text before or after).

    Respond ONLY with valid JSON in this format:
    {{ "symptoms": [<list of symptoms>] }}

    Possible symptoms:
    ["abdominal_pain", "anxiety", "blurred_vision", "chest_pain", "cough", "diarrhea", 
    "difficulty_breathing", "difficulty_concentrating", "dizziness", "dry_skin", "ear_pain", 
    "facial_pain", "fatigue", "fever", "frequent_urination", "headache", "heartburn", 
    "increased_thirst", "itchy_eyes", "joint_pain", "loss_of_taste_smell", "nausea", 
    "night_sweats", "painful_urination", "pale_skin", "rash", "restlessness", "runny_nose", 
    "sadness", "sneezing", "sore_throat", "swollen_lymph_nodes", "vomiting", "weight_loss", "wheezing"]

    ---
    Medical Note:
    {notes}
    """,
    format=Symptoms)

    vital_signs = get_response(model,f"""
You are a strict information extraction system.

Extract only the information that is explicitly stated or directly implied in the following medical note. 
If a field or value is not mentioned, omit it completely from the JSON output. 
Do NOT infer, guess, or add information that is not in the note.

Return ONLY valid JSON (no text before or after).

    Schema:
    {{
    "vital_signs": {{
        "blood_pressure": {{
        "systolic": {{ "value": <number>, "unit": "mmHg" }},
        "diastolic": {{ "value": <number>, "unit": "mmHg" }}
        }},
        "heart_rate": {{ "value": <number>, "unit": "bpm" }},
        "oxygen_saturation": {{ "value": <number>, "unit": "%" }},
        "cholesterol_level": {{ "value": <number>, "unit": "mg/dL" }},
        "glucose_level": {{ "value": <number>, "unit": "mg/dL" }},
        "temperature": {{ "value": <number>, "unit": "°C" }},
        "respiratory_rate": {{ "value": <number>, "unit": "breaths/min" }}
    }}
    }}

    ---
    Medical Note:
    {notes}
    """,
    format=VitalSigns)

    visit_motivation_json = json.loads(visit_motivation.model_dump_json())
    symptoms_json = json.loads(symptoms.model_dump_json())
    vital_signs_json = json.loads(vital_signs.model_dump_json())

    vital_signs_json = {
        key: value for key, value in vital_signs_json.items()
        if value is not None  # Remove direct None values like "temperature": None
        and value != {}  # Remove empty dicts
        and not (isinstance(value, dict) and value.get('value') is None)  # Remove nested None values
    }

    # Combine into a single response object
    response = {
        **visit_motivation_json,  # Contains "patient_info" and "visit_motivation"
        **symptoms_json,          # Contains "symptoms"
        "vital_signs": vital_signs_json        # Contains "vital_signs"
    }

    return json.dumps(response, separators=(',', ':'))

def response_grabber(model, notes):
    return get_response(model, system_prompt="""
You are a medical information extraction AI. Convert unstructured clinical notes into a STRICT JSON object that conforms to the schema and rules below.

OVERALL CONTRACT
- Parse ONLY what is explicitly stated in the notes.
- Do NOT infer, diagnose, or guess.
- Output MUST be a single valid JSON object (UTF-8), with no comments, no surrounding prose, and no code fences.
- Omit any field that is unavailable or not explicitly present.
- Use exact enum values and exact units as specified.

SCHEMA (allowed keys and shapes)
{
  "patient_info": {
    "age": number,
    "gender": "Female" | "Male"
  },
  "visit_motivation": one of [
    "Allergies","Anemia","Anxiety Disorders","Asthma","COVID-19",
    "Chronic Obstructive Pulmonary Disease (COPD)","Common Cold","Depression",
    "Diabetes (Type 2)","Ear Infection (Otitis Media)","Eczema (Atopic Dermatitis)",
    "Gastroesophageal Reflux Disease (GERD)","Heart Disease (Coronary Artery Disease)",
    "Hypertension (High Blood Pressure)","Influenza (Flu)","Pneumonia",
    "Sinusitis","Strep Throat","Tuberculosis (TB)","Urinary Tract Infection (UTI)"
  ],
  "symptoms": array of strings, each item must be exactly one of:
    [
      "abdominal_pain","anxiety","blurred_vision","chest_pain","cough","diarrhea",
      "difficulty_breathing","difficulty_concentrating","dizziness","dry_skin",
      "ear_pain","facial_pain","fatigue","fever","frequent_urination","headache",
      "heartburn","increased_thirst","itchy_eyes","joint_pain","loss_of_taste_smell",
      "nausea","night_sweats","painful_urination","pale_skin","rash","restlessness",
      "runny_nose","sadness","sneezing","sore_throat","swollen_lymph_nodes",
      "vomiting","weight_loss","wheezing"
    ],
  "vital_signs": {
    "temperature": { "value": number, "unit": "°C" | "°F" },
    "blood_pressure": {
      "systolic":  { "value": number, "unit": "mmHg" },
      "diastolic": { "value": number, "unit": "mmHg" }
    },
    "heart_rate":        { "value": number, "unit": "bpm" },
    "respiratory_rate":  { "value": number, "unit": "breaths/min" },
    "oxygen_saturation": { "value": number, "unit": "%" },
    "glucose_level":     { "value": number, "unit": "mg/dL" },
    "cholesterol_level": { "value": number, "unit": "mg/dL" }
  }
}

CRITICAL RULES
1. Output ONLY a JSON object — no prose, no code fences, no comments.
2. Include ONLY keys from the schema (patient_info, visit_motivation, symptoms, vital_signs).
3. Use proper nested objects — never dotted keys.
4. Extract values ONLY if explicitly stated in the notes. Do not infer.
5. ABSOLUTELY NO null/NULL/None anywhere in the JSON. If a value is unknown, OMIT the entire key.
6. Do NOT emit placeholder values (0, -1, "", NaN, Infinity) for missing data.
7. Arrays (like symptoms) must not be empty; if no items, omit the array entirely.
8. Numeric fields must be numbers, not strings.
9. Ensure valid JSON formatting.

ATOMICITY (vital_signs)
- Emit a measurement ONLY if you have ALL required subfields:
  - temperature: value AND unit → otherwise omit.
  - blood_pressure: BOTH systolic AND diastolic complete → otherwise omit blood_pressure.
  - heart_rate / respiratory_rate / oxygen_saturation / glucose_level / cholesterol_level:
    each requires value AND unit; otherwise omit the measurement.
- If vital_signs is empty after omissions, omit vital_signs.

SECTION-AWARE, EXHAUSTIVE SCAN
- Scan ALL parts of the note (header/demographics, chief complaint, HPI, ROS, PMH/PSH, meds, allergies, triage sheet, vitals section, physical exam, assessment/plan, discharge summary, signature/footer, tables/templates).
- Pay special attention to compact header lines and triage lines.

ROBUST DEMOGRAPHIC PATTERNS (EXPLICIT ONLY; case-insensitive)
- Age: “56-year-old”, “56 yo”, “56yo”, “56 yrs”, “Age: 56”, “56 y/o”, “56 yr old”, “56 y.o.”
- Gender tokens/abbreviations:
  - “Gender: Male/Female”, “Sex: M/F”, solitary “Male”/“Female”, “M”/“F” when adjacent to age or demographic tokens (e.g., “56yo M”, “F, 34 yo”, “M presents with…”).
  - Titles/pronouns when clearly referring to the patient: “Mr.” → Male; “Mrs.”/“Ms.”/“Miss” → Female; “he/him/his” → Male; “she/her/hers” → Female.
  - Terms: “man”, “woman” used about the patient.
- DO NOT infer from names or relationships.

DISAMBIGUATION & PRIORITY
- If conflicting tokens occur, prefer the explicit demographic/header line over narrative mentions; prefer the LAST explicit demographic mention.
- Pronouns count ONLY if they clearly refer to the patient.

MANDATED SECOND PASS (BEFORE EMITTING JSON)
- Perform a dedicated re-scan specifically to find gender and age using the above pattern library across headers, triage lines, and signature blocks.
- If gender or age is explicitly present, you MUST include it in patient_info.
- If not explicitly present, omit the key(s); do NOT guess.

SELF-AUDIT CHECKLIST (internal)
- [ ] No null/placeholder values.
- [ ] Every vital has value+unit; otherwise removed.
- [ ] Gender/age re-scanned and included if explicitly present.
- [ ] No empty arrays/objects remain.
- [ ] JSON parses successfully.

EMPTY OUTPUT
If no extractable data per schema → return {}
""", user_prompt=f"""Extract structured medical data from the following clinical note according to the schema and rules defined in the system prompt.

<<<NOTES
{notes}
NOTES""")

def get_json_full(model, notes):
    max_attempts = 3
    for attempt in range(max_attempts):
        response = response_grabber(model, notes)
        try:
            data = json.loads(response)
            break  
        except json.JSONDecodeError:
            if attempt == max_attempts - 1:
                # Last attempt failed
                raise ValueError(f"Failed to get valid JSON after {max_attempts} attempts")
            # Loop

    # --- Strict vital signs cleanup ---
    if "vital_signs" in data:
        vital_signs = data["vital_signs"]
        cleaned_vitals = {}

        # Blood pressure logic
        bp = vital_signs.get("blood_pressure", {})
        systolic_val = bp.get("systolic", {}).get("value")
        diastolic_val = bp.get("diastolic", {}).get("value")

        # Keep systolic/diastolic only if valid
        bp_clean = {}
        if systolic_val not in [None, "#", "", "null"]:
            bp_clean["systolic"] = bp["systolic"]
        if diastolic_val not in [None, "#", "", "null"]:
            bp_clean["diastolic"] = bp["diastolic"]

        # Only keep blood_pressure if at least one exists
        if bp_clean:
            cleaned_vitals["blood_pressure"] = bp_clean

        # Process all other vital signs
        for key, val in vital_signs.items():
            if key == "blood_pressure":
                continue
            if isinstance(val, dict):
                v = val.get("value")
                if v not in [None, "#", "", "null"]:
                    cleaned_vitals[key] = val

        data["vital_signs"] = cleaned_vitals

    # Validate correct JSON
    return json.dumps(data, separators=(',', ':'))

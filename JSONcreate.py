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



def get_json_full(model, notes):
    response = get_response(model, f"""
You are a strict information extraction system.

Extract only the information that is explicitly stated or directly implied in the following medical note. 
If a field or value is not mentioned, omit it completely from the JSON output. 
Do NOT infer, guess, or add information that is not in the note.

Return ONLY valid JSON (no text before or after).

Use this schema:
{{
  "patient_info": {{
    "age": <number>,
    "gender": "Male" | "Female"
  }},
  "visit_motivation": <string>,  # single best matching condition from the list below
  "symptoms": [<list of mentioned symptoms>],
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

Only include vital sign entries that appear in the note; if neither systolic nor diastolic pressure is given, omit "blood_pressure" entirely.

Possible values for "visit_motivation" are:
["Anemia", "Allergies", "Diabetes (Type 2)", "Tuberculosis (TB)", "Depression", "Asthma",
"Hypertension (High Blood Pressure)", "Influenza (Flu)", "Anxiety Disorders", 
"Gastroesophageal Reflux Disease (GERD)", "Heart Disease (Coronary Artery Disease)", 
"Pneumonia", "Urinary Tract Infection (UTI)", "Common Cold", "Ear Infection (Otitis Media)",
"Eczema (Atopic Dermatitis)", "COVID-19", "Strep Throat", "Sinusitis", "Chronic Obstructive Pulmonary Disease (COPD)"]

Possible "symptoms" keys are:
["abdominal_pain", "anxiety", "blurred_vision", "chest_pain", "cough", "diarrhea", 
"difficulty_breathing", "difficulty_concentrating", "dizziness", "dry_skin", "ear_pain", 
"facial_pain", "fatigue", "fever", "frequent_urination", "headache", "heartburn", 
"increased_thirst", "itchy_eyes", "joint_pain", "loss_of_taste_smell", "nausea", 
"night_sweats", "painful_urination", "pale_skin", "rash", "restlessness", "runny_nose", 
"sadness", "sneezing", "sore_throat", "swollen_lymph_nodes", "vomiting", "weight_loss", "wheezing"]

---
Medical Notes:
{notes}
""")
    
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        start = response.find('{')
        end = response.rfind('}') + 1
        json_str = response[start:end]
        data = json.loads(json_str)

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


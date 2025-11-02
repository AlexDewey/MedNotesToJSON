import json

from LLMAPIs import get_response

def get_json(model, notes):
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
    
    # For vital signs that have null values, remove them from the JSON

    # Try parsing the JSON safely
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


# {"patient_info":
#  {"age": 41, "gender": "Male"},
#  "visit_motivation": "Anemia",
#  "symptoms": ["fever", "fatigue", "difficulty_breathing", "vomiting", "dizziness", "blurred_vision", "wheezing", "pale_skin"],
#  "vital_signs":{
#     "heart_rate": {"value": 114, "unit": "bpm"},
#     "oxygen_saturation": {"value": 98.4, "unit": "%"},
#     "cholesterol_level": {"value": 132.8, "unit": "mg/dL"},
#     "glucose_level": {"value": 110.6, "unit": "mg/dL"}
#     }}

# {"patient_info"
# {"age": 56, "gender": "Male"},
# "visit_motivation": "Allergies",
# "symptoms": ["runny_nose", "sneezing", "itchy_eyes", "blurred_vision", "wheezing"],
# "vital_signs":{
#     "temperature": {"value": 36.6, "unit": "\u00b0C"},
#     "respiratory_rate": {"value": 13, "unit": "breaths/min"},
#     "glucose_level": {"value": 99.0, "unit": "mg/dL"}
# }}

    # age = get_response(model, "Only return the age of patient: " + medData)
    # gender = get_response(model, "Only return the gender of patient: " + medData)
    # visit_motivation = get_response(model, "Only return the visit motivation of patient: " + medData)
    # symptoms = get_response(model, "Only return the symptoms of patient as a python string list: " + medData)
    # vital_signs = get_response(model, "Only return a python list of all vital signs recorded from options" \
    #                                   "'heart_rate', 'oxygen_saturation', 'cholesterol_level', 'glucose_level', 'temperature', 'respiratory_rate', : " + medData)

    # # Process vital_signs into a list to iterate through
    # vital_signs_list = vital_signs.strip("[]").split(", ")
    # for vital_sign in vital_signs_list:
    #     value = get_response(model, f"Only return the value of {vital_sign} as a number: " + medData)
    #     unit = get_response(model, f"Only return the unit of {vital_sign}: " + medData)
    #     vital_signs = vital_signs.replace(vital_sign, f'"{vital_sign}": {{"value": {value}, "unit": "{unit}"}}')

    # # Stich together all variables into a JSON string
    # json_string = f'{{"patient_info": {{"age": {age}, "gender": "{gender}"}}, "visit_motivation": "{visit_motivation}", "symptoms": {symptoms}, "vital_signs": {{{vital_signs}}}}}'


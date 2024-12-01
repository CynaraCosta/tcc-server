from ..connection import db
from ..utils.loadJson import load_json
from embedding import generate_embedding

def patientEmbeddings(patient):
    embeddings = {}

    # patient_info 
    patient_info_text = (
        f"ID: {patient['_id']}, "
        f"Nome: {patient['patient_info'].get('name', 'Sem nome')}, "
        f"Data de nascimento: {patient['patient_info'].get('birth_date', 'Sem data')}, "
        f"Gênero: {patient['patient_info'].get('gender', 'Sem gênero')}, "
        f"Endereço: {patient['patient_info'].get('address', 'Sem endereço')}, "
        f"Telefone: {patient['patient_info'].get('phone', 'Sem telefone')}, "
        f"Convênio: {patient['patient_info'].get('insurance', 'Sem convênio')}"
    )
    embeddings["patient_info"] = generate_embedding(patient_info_text)

    # medical_history
    chronic_conditions = ", ".join(patient['medical_history'].get('chronic_conditions', []))
    allergies = ", ".join(patient['medical_history'].get('allergies', []))
    surgeries = ", ".join(patient['medical_history'].get('surgeries', []))
    current_medications = ", ".join(patient['medical_history'].get('current_medications', []))

    medical_history_text = (
        f"Doenças crônicas: {chronic_conditions}. "
        f"Alergias: {allergies}. "
        f"Cirurgias: {surgeries}. "
        f"Medicações atuais: {current_medications}."
    )
    embeddings["medical_history"] = generate_embedding(medical_history_text)

    # consultations
    consultations_embeddings = []
    for consultation in patient["consultations"]:
        consultation_text = (
            f"ID: {patient['_id']}, "
            f"Data: {consultation.get('date', 'Sem data')}, "
            f"Motivo: {consultation.get('reason', 'Sem motivo')}, "
            f"Sintomas: {', '.join(consultation.get('symptoms', []))}, "
            f"Exames solicitados: {', '.join(consultation.get('exams_requested', []))}, "
            f"Instruções: {', '.join(consultation.get('instructions', []))}"
        )
        consultations_embeddings.append(generate_embedding(consultation_text))
    embeddings["consultations_embeddings"] = consultations_embeddings

    # vaccine_info
    vaccines = ", ".join(patient["vaccine_info"].get("vaccines", []))
    vaccine_info_text = f"Vacinas: {vaccines}."
    embeddings["vaccine_info"] = generate_embedding(vaccine_info_text)

    return embeddings

def patientInsert(patientJsonPath):
    patient = load_json(patientJsonPath)
    embeddings = patientEmbeddings(patient)

    patient["patient_info"]["embedding"] = embeddings["patient_info"]
    patient["medical_history_embedding"] = embeddings["medical_history"]
    patient["consultations_embeddings"] = embeddings["consultations_embeddings"]
    patient["vaccine_info"]["embedding"] = embeddings["vaccine_info"]
    
    db.patients.insert_one(patient)
    print(f"Paciente {patient['_id']} inserido com sucesso!")
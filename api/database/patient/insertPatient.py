from ..connection import db
from ..utils.loadJson import load_json
from embedding import generate_embedding

def format_patient_info(patient_info):
    return (
        f"Nome: {patient_info.get('name', 'Sem nome')}. "
        f"Data de nascimento: {patient_info.get('birth_date', 'Sem data')}. "
        f"Gênero: {patient_info.get('gender', 'Sem gênero')}. "
        f"Endereço: {patient_info.get('address', 'Sem endereço')}. "
        f"Telefone: {patient_info.get('phone', 'Sem telefone')}. "
        f"Convênio: {patient_info.get('insurance', 'Sem convênio')}. "
    )

def format_medical_history(patient):
    return (
        f"Doenças crônicas: {', '.join(patient.get('chronic_conditions', []))}. "
        f"Alergias: {', '.join(patient.get('allergies', []))}. "
        f"Cirurgias: {', '.join(patient.get('surgeries', []))}. "
        f"Medicações atuais: {', '.join(patient.get('current_medications', []))}. "
    )

def format_consultations(consultations):
    consultations_text = []
    for c in consultations:
        consultation_info = (
            f"Data: {c.get('date', 'Sem data')}, "
            f"Motivo: {c.get('reason', 'Sem motivo')}, "
            f"Sintomas: {', '.join(c.get('symptoms', []))}, "
            f"Exames solicitados: {', '.join(c.get('exams_requested', []))}, "
            f"Instruções: {', '.join(c.get('instructions', []))}"
        )
        consultations_text.append(consultation_info)
    return f"Consultas: {' | '.join(consultations_text)}. "

def format_vaccines(patient_info):
    return f"Vacinas: {', '.join(patient_info.get('vaccines', []))}. "

def generate_patient_embedding(patient):
    consolidated_text = (
        f"ID: {patient['_id']}. "
        + format_patient_info(patient['patient_info'])
        + format_medical_history(patient)
        + format_consultations(patient.get('consultations', []))
        + format_vaccines(patient['patient_info'])
    )

    return generate_embedding(consolidated_text)

def patientInsert(patient):
    # patient = load_json(patientJsonPath)
    embeddings = generate_patient_embedding(patient)

    patient["patient_embeddings"] = embeddings
    
    db.patients.insert_one(patient)
    print(f"Paciente {patient['_id']} inserido com sucesso!")
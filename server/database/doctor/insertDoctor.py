from ..connection import db
from ..utils.loadJson import load_json
from embedding import generate_embedding

# def doctorEmbeddings(doctor):
#     text = (
#         f"Nome: {doctor.get('name', 'Sem nome')}, "
#         f"E-mail: {doctor.get('email', 'Sem email')}, "
#         f"Especialidade: {doctor.get('specialty', 'Sem especialidade')}, "
#         f"Hospital: {doctor.get('hospital', 'Sem hospital')}, "
#         f"Pacientes: {', '.join(doctor.get('patients', []))}"
#     )
#     embedding = generate_embedding(text)
#     return embedding

def doctorInsert(doctorJsonPath):
    doctor = load_json(doctorJsonPath)
    # doctor_embedding = doctorEmbeddings(doctor)
    # doctor['embedding'] = doctor_embedding
    db.users.insert_one(doctor)
    print(f"Médico {doctor['_id']} inserido com sucesso!")

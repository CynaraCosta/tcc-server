from database.patient.insertPatient import patientInsert
from database.doctor.insertDoctor import doctorInsert
from database.conversation.insertConversation import conversationInsert

if __name__ == "__main__":
    doctor_path = "mocks/doctor_mock.json"
    patient_path = "mocks/patient_mock.json"
    conversation_path = "mocks/conversation_mock.json"
    
    # doctorInsert(doctor_path)
    # patientInsert(patient_path)
    # conversationInsert(conversation_path)
from gemini import query_data
import numpy as np

def evaluate_rag(test_queries, ground_truths, K=5):
    """
    Avalia o desempenho do RAG usando Recall@K e NDCG@K.

    test_queries: Lista de perguntas de teste.
    mock_documents: Lista de respostas esperadas (documentos relevantes).
    K: Número de documentos recuperados.
    """
    recall_scores = []
    ndcg_scores = []

    for i, query in enumerate(test_queries):
        retrieved_docs = query_data(query, eval_mode=True)  # Busca os documentos
        
        relevant_docs = set(ground_truths[i])  # Documentos esperados
        retrieved_doc_ids = [doc.metadata["_id"] for doc in retrieved_docs[:K]]  # Pega IDs dos K primeiros

        # **📌 Cálculo do Recall@K**
        retrieved_relevant_docs = len(relevant_docs.intersection(retrieved_doc_ids))
        recall_at_k = retrieved_relevant_docs / len(relevant_docs) if len(relevant_docs) > 0 else 0
        recall_scores.append(recall_at_k)

        # **📌 Cálculo do NDCG**
        relevance_scores = [1 if doc_id in relevant_docs else 0 for doc_id in retrieved_doc_ids]
        dcg = np.sum([rel / np.log2(idx + 2) for idx, rel in enumerate(relevance_scores)])
        idcg = np.sum([1 / np.log2(idx + 2) for idx in range(len(relevant_docs))]) if len(relevant_docs) > 0 else 1
        ndcg = dcg / idcg if idcg > 0 else 0
        ndcg_scores.append(ndcg)

    avg_recall = np.mean(recall_scores)
    avg_ndcg = np.mean(ndcg_scores)

    print(f"📊 **Resultados da Avaliação:**")
    print(f"Recall@{K}: {avg_recall:.4f}")
    print(f"NDCG@{K}: {avg_ndcg:.4f}")

    return {"recall": avg_recall, "ndcg": avg_ndcg}

test_queries = [
    "Quais vacinas o paciente João recebeu?",
    "Qual foi a última consulta do paciente Maria?",
]

mock_documents = [
    {
        "_id": "doc1",
        "patient_name": "João Silva",
        "medical_history": "Paciente diagnosticado com hipertensão em 2021. Faz uso de medicação controlada.",
        "last_consultation": "10/03/2024 - Consulta de rotina. Pressão arterial normal.",
        "vaccines": ["Hepatite B", "COVID-19", "Febre Amarela"],
        "patient_embeddings": [0.12, 0.45, 0.88, 0.33],  # Simulação de embeddings
    },
    {
        "_id": "doc2",
        "patient_name": "João Silva",
        "medical_history": "Histórico de alergias leves a frutos do mar.",
        "last_consultation": "15/05/2024 - Exame de sangue realizado. Nenhuma alteração significativa.",
        "vaccines": ["Gripe", "Dengue"],
        "patient_embeddings": [0.11, 0.49, 0.87, 0.32],
    },
    {
        "_id": "doc3",
        "patient_name": "Maria Oliveira",
        "medical_history": "Paciente com histórico de diabetes tipo 2. Em acompanhamento nutricional.",
        "last_consultation": "22/02/2024 - Ajuste de medicação para controle glicêmico.",
        "vaccines": ["Hepatite A", "HPV"],
        "patient_embeddings": [0.18, 0.55, 0.78, 0.29],
    }
]

evaluate_rag(test_queries, mock_documents)
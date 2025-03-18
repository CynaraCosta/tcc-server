from .gemini import query_data
import numpy as np
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.json_loader import JSONLoader
import json

def generate_mocks():
    loader = DirectoryLoader(
        './patients_mocks',
        glob='./*.json',
        show_progress=True,
        loader_cls=JSONLoader,
        loader_kwargs={'jq_schema': '.', 'text_content': False}
    )
    raw_data = loader.load()

    mock_ground_truth = {}
    for doc in raw_data:
        data = json.loads(doc.page_content) 
        mock_ground_truth[data["_id"]] = data
    return mock_ground_truth

test_queries = [
    "Quais vacinas o paciente João Silva recebeu?",
    "Qual foi a última consulta do paciente Maria Oliveira?",
]

mock_documents = generate_mocks()

def evaluate_rag(test_queries, ground_truths, K=5):
    """
    Avalia o desempenho do RAG usando Recall@K e NDCG@K.
    
    test_queries: Lista de queries de teste.
    ground_truths: Dicionário com a ground truth (relevância) para cada documento.
    K: Número de documentos recuperados.
    """
    recall_scores = []
    ndcg_scores = []
    
    # Como não há mapeamento direto entre query e ground truth,
    # usaremos os dois primeiros _ids dos documentos como exemplos de ground truth para cada query.
    ground_truth_ids = list(ground_truths.keys())
    
    for i, query in enumerate(test_queries):
        retrieved_docs = query_data(query)
        
        # Para cada query, pegamos o i-ésimo documento como ground truth (ajuste conforme sua lógica)
        relevant_doc = ground_truth_ids[i] if i < len(ground_truth_ids) else None
        relevant_docs = {relevant_doc} if relevant_doc is not None else set()
        
        print(f'CYNARA {retrieved_docs}')
        # Extraia os _ids dos documentos recuperados usando metadata
        retrieved_doc_ids = [doc.metadata["_id"] for doc in retrieved_docs[:K]]
        
        # Cálculo do Recall@K
        retrieved_relevant_docs = len(relevant_docs.intersection(retrieved_doc_ids))
        recall_at_k = retrieved_relevant_docs / len(relevant_docs) if len(relevant_docs) > 0 else 0
        recall_scores.append(recall_at_k)
        
        # Cálculo do NDCG@K
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

evaluate_rag(test_queries, mock_documents)
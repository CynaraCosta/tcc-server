import math
import json
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.json_loader import JSONLoader
from .gemini import query_data  # sua função que chama o RAG


def generate_mocks():
    """
    Carrega os arquivos dos mocks e retorna um dicionário com os dados,
    onde a chave é o _id do documento.
    """
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


def get_ground_truth_for_query(query, mocks):
    """
    Considera que todos os documentos dos mocks são relevantes para qualquer query.
    """
    return list(mocks.keys())


def recall_at_k(retrieved_docs, ground_truth, k):
    """
    Calcula o Recall@K:
      (# de documentos relevantes nos top k) / (total de documentos relevantes)
    """
    retrieved_k = retrieved_docs[:k]
    relevant_retrieved = sum(1 for doc in retrieved_k if doc in ground_truth)
    total_relevant = len(ground_truth)
    return relevant_retrieved / total_relevant if total_relevant > 0 else 0


def dcg_at_k(relevances, k):
    """
    Calcula o DCG@K.
    Para cada posição i, a contribuição é (2^rel - 1) / log2(i+2)
    """
    return sum((2 ** rel - 1) / math.log2(idx + 2) for idx, rel in enumerate(relevances[:k]))


def ndcg_at_k(retrieved_docs, ground_truth, k):
    """
    Calcula o NDCG@K usando relevância binária:
      1 se o documento estiver na ground truth, 0 caso contrário.
    """
    relevances = [1 if doc in ground_truth else 0 for doc in retrieved_docs]
    dcg = dcg_at_k(relevances, k)
    ideal_relevances = sorted(relevances, reverse=True)
    idcg = dcg_at_k(ideal_relevances, k)
    return dcg / idcg if idcg > 0 else 0


def evaluate_queries(test_queries, k=3):
    """
    Para cada query de teste, utiliza os mocks para derivar a ground truth,
    chama a função query_data do RAG e avalia com Recall@K e NDCG@K.
    """
    mocks = generate_mocks()

    for query in test_queries:
        # Para cada query, a ground truth é todos os documentos dos mocks
        ground_truth = get_ground_truth_for_query(query, mocks)

        # Chama a função do seu RAG que retorna (resposta, [IDs dos documentos])
        response, retrieved_ids = query_data(query)

        rec = recall_at_k(retrieved_ids, ground_truth, k)
        ndcg = ndcg_at_k(retrieved_ids, ground_truth, k)

        print(f"\nQuery: {query}")
        print(f"Resposta: {response}")
        print(f"Documentos retornados: {retrieved_ids}")
        print(f"Recall@{k}: {rec:.2f}")
        print(f"NDCG@{k}: {ndcg:.2f}\n")


if __name__ == '__main__':
    # Exemplo de queries de teste
    test_queries = [
        "Quais vacinas o paciente João Silva recebeu?",
        "Qual foi a última consulta do paciente Maria Oliveira?",
        "Qual o plano de saúde do paciente João?",
    ]
    evaluate_queries(test_queries, k=3)

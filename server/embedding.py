from config import Config
import requests

hf_token = Config.HF_TOKEN
embedding_url = 'https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2'


def generate_embedding(sentence: str) -> list[float]:
    response = requests.post(
        embedding_url,
        headers={'Authorization': f'Bearer {hf_token}'},
        json={"inputs": sentence}
    )

    if response.status_code != 200:
        raise ValueError(
            f'Request failed with status code {response.status_code}: {response.text}')

    return response.json()

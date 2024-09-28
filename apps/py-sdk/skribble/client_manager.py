from .client import SkribbleClient

_client = None

def init(username: str, api_key: str):
    global _client
    _client = SkribbleClient(username, api_key)

def get_client() -> SkribbleClient:
    if _client is None:
        raise ValueError("Skribble SDK not initialized. Call skribble.init(username, api_key) first.")
    return _client
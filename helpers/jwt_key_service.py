import time
import requests
from django.conf import settings


class PublicKeyCache:
    """
    Cache the public key fetched from the Auth server to reduce repeated network calls.
    """
    _cache = None
    _last_fetched = 0
    _ttl = 3600  # 1 hour cache

    @classmethod
    def get_public_key(cls):
        current_time = time.time()
        if cls._cache and (current_time - cls._last_fetched) < cls._ttl:
            return cls._cache

        try:
            url = settings.AUTH_SERVER_URL.rstrip("/") + "/api/public-key/"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            secret_key = data.get("secret_key", "")
            algorithm = "HS256"

            cls._cache = {"key": secret_key, "algorithm": algorithm}
            cls._last_fetched = current_time
            return cls._cache

        except Exception as e:
            raise Exception(f"Failed to fetch secret_key from Auth Server: {e}")
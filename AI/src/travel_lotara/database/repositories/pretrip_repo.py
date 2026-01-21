# travel_lotara/database/repositories/pretrip_repo.py

from datetime import datetime, timedelta
from ..client import SupabaseClient

class PreTripRepository:
    def __init__(self):
        self.db = SupabaseClient.get_client()

    # ---------- Generic cache ----------
    def _make_key(self, category: str, **kwargs) -> str:
        suffix = "_".join(f"{k}:{v}" for k, v in kwargs.items())
        return f"{category}:{suffix}"

    def get_cached(self, cache_key: str):
        res = (
            self.db
            .table("pretrip_cache")
            .select("value, expires_at")
            .eq("cache_key", cache_key)
            .limit(1)
            .execute()
        )

        if not res.data:
            return None

        record = res.data[0]
        if record["expires_at"] and datetime.fromisoformat(record["expires_at"]) < datetime.utcnow():
            return None

        return record["value"]

    def save_cached(self, cache_key: str, value: dict, ttl_days: int = 7):
        expires_at = datetime.utcnow() + timedelta(days=ttl_days)

        self.db.table("pretrip_cache").upsert({
            "cache_key": cache_key,
            "value": value,
            "expires_at": expires_at.isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }).execute()

    # ---------- Visa ----------
    def get_visa(self, nationality: str, destination: str):
        key = self._make_key("visa", nationality=nationality, destination=destination)
        return self.get_cached(key)

    def save_visa(self, nationality: str, destination: str, visa_info: dict):
        key = self._make_key("visa", nationality=nationality, destination=destination)
        self.save_cached(key, visa_info, ttl_days=30)

    # ---------- Medical ----------
    def get_medical(self, destination: str):
        key = self._make_key("medical", destination=destination)
        return self.get_cached(key)

    def save_medical(self, destination: str, info: dict):
        key = self._make_key("medical", destination=destination)
        self.save_cached(key, info, ttl_days=30)

    # ---------- Travel Advisory ----------
    def get_advisory(self, destination: str):
        key = self._make_key("advisory", destination=destination)
        return self.get_cached(key)

    def save_advisory(self, destination: str, info: dict):
        key = self._make_key("advisory", destination=destination)
        self.save_cached(key, info, ttl_days=7)

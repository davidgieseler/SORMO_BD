import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import orjson
from loguru import logger

from config import Config


class CacheService:
    def __init__(self):
        self.cache_dir = Path(Config.CACHE_DIR)
        self.routes_dir = self.cache_dir / "routes"
        self.osm_dir = self.cache_dir / "osm"
        self.toll_dir = self.cache_dir / "toll"
        self.weather_dir = self.cache_dir / "weather"
        self.ensure_directories()

    def ensure_directories(self):
        for directory in [self.routes_dir, self.osm_dir, self.toll_dir, self.weather_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def generate_key(self, data: Dict[str, Any]) -> str:
        normalized = orjson.dumps(data, option=orjson.OPT_SORT_KEYS)
        return normalized.hex()

    def get(self, key: str, cache_type: str = "routes", max_age_seconds: Optional[int] = None) -> Optional[Dict]:
        cache_dir = self._get_cache_dir(cache_type)
        cache_file = cache_dir / f"{key}.json"
        if not cache_file.exists():
            return None

        try:
            raw = cache_file.read_bytes()
            cached_data = orjson.loads(raw)
            created_at = cached_data.get("created_at", 0)
            ttl = max_age_seconds if max_age_seconds is not None else self._get_default_ttl(cache_type)
            if ttl and (time.time() - created_at) > ttl:
                cache_file.unlink(missing_ok=True)
                return None
            return cached_data.get("data")
        except Exception as exc:
            logger.error(f"Erro ao ler cache {key}: {exc}")
            return None

    def set(self, key: str, data: Dict, cache_type: str = "routes") -> bool:
        cache_dir = self._get_cache_dir(cache_type)
        cache_file = cache_dir / f"{key}.json"
        try:
            payload = {"created_at": time.time(), "data": data}
            cache_file.write_bytes(orjson.dumps(payload))
            self._update_index(cache_dir)
            return True
        except Exception as exc:
            logger.error(f"Erro ao salvar cache {key}: {exc}")
            return False

    def invalidate(self, key: str, cache_type: str = "routes") -> bool:
        cache_dir = self._get_cache_dir(cache_type)
        cache_file = cache_dir / f"{key}.json"
        try:
            if cache_file.exists():
                cache_file.unlink()
                self._update_index(cache_dir)
                return True
            return False
        except Exception as exc:
            logger.error(f"Erro ao invalidar cache {key}: {exc}")
            return False

    def clear_expired(self, cache_type: Optional[str] = None) -> int:
        removed = 0
        cache_types = [cache_type] if cache_type else ["routes", "osm", "toll", "weather"]
        for ctype in cache_types:
            directory = self._get_cache_dir(ctype)
            ttl = self._get_default_ttl(ctype)
            for file in directory.glob("*.json"):
                try:
                    raw = file.read_bytes()
                    data = orjson.loads(raw)
                    created_at = data.get("created_at", 0)
                    if ttl and (time.time() - created_at) > ttl:
                        file.unlink(missing_ok=True)
                        removed += 1
                except Exception as exc:
                    logger.warning(f"Erro limpando cache {file}: {exc}")
        return removed

    def get_stats(self) -> Dict[str, Dict[str, float]]:
        stats: Dict[str, Dict[str, float]] = {}
        for name in ["routes", "osm", "toll", "weather"]:
            directory = self._get_cache_dir(name)
            size_bytes = sum(f.stat().st_size for f in directory.glob("*.json")) if directory.exists() else 0
            count_files = len(list(directory.glob("*.json"))) if directory.exists() else 0
            stats[name] = {"files": count_files, "size_mb": round(size_bytes / (1024 * 1024), 3)}
        return stats

    def _get_cache_dir(self, cache_type: str) -> Path:
        mapping = {
            "routes": self.routes_dir,
            "osm": self.osm_dir,
            "toll": self.toll_dir,
            "weather": self.weather_dir,
        }
        return mapping.get(cache_type, self.routes_dir)

    def _get_default_ttl(self, cache_type: str) -> int:
        mapping = {
            "routes": Config.CACHE_ROUTES_TTL,
            "osm": Config.CACHE_OSM_TTL,
            "toll": Config.CACHE_TOLL_TTL,
            "weather": Config.CACHE_WEATHER_TTL,
        }
        return mapping.get(cache_type, Config.CACHE_ROUTES_TTL)

    def _update_index(self, cache_dir: Path):
        index_file = cache_dir / "index.json"
        items = [f.name for f in cache_dir.glob("*.json")]
        try:
            index_file.write_bytes(orjson.dumps({"updated_at": datetime.utcnow().isoformat(), "items": items}))
        except Exception as exc:
            logger.warning(f"Nao foi possivel atualizar indice em {cache_dir}: {exc}")

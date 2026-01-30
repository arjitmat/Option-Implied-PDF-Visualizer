"""
Data caching layer to reduce API calls and improve performance.
"""

import os
import json
import pickle
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from functools import wraps


class DataCache:
    """Simple file-based cache for data fetching."""

    def __init__(self, cache_dir: str = ".cache", ttl_minutes: int = 15):
        """
        Initialize data cache.

        Args:
            cache_dir: Directory to store cache files
            ttl_minutes: Time-to-live for cached data in minutes
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(minutes=ttl_minutes)

    def _get_cache_path(self, key: str) -> Path:
        """Get path for cache file."""
        # Sanitize key for filesystem
        safe_key = key.replace('/', '_').replace(':', '_').replace(' ', '_')
        return self.cache_dir / f"{safe_key}.pkl"

    def _get_metadata_path(self, key: str) -> Path:
        """Get path for metadata file."""
        safe_key = key.replace('/', '_').replace(':', '_').replace(' ', '_')
        return self.cache_dir / f"{safe_key}_meta.json"

    def get(self, key: str) -> Optional[Any]:
        """
        Get data from cache if it exists and is not expired.

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found or expired
        """
        cache_path = self._get_cache_path(key)
        meta_path = self._get_metadata_path(key)

        # Check if cache exists
        if not cache_path.exists() or not meta_path.exists():
            return None

        try:
            # Read metadata
            with open(meta_path, 'r') as f:
                metadata = json.load(f)

            # Check if expired
            cached_time = datetime.fromisoformat(metadata['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                # Cache expired, remove files
                cache_path.unlink(missing_ok=True)
                meta_path.unlink(missing_ok=True)
                return None

            # Read cached data
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)

            return data

        except Exception as e:
            print(f"Warning: Failed to read cache for {key}: {str(e)}")
            return None

    def set(self, key: str, data: Any) -> None:
        """
        Store data in cache.

        Args:
            key: Cache key
            data: Data to cache
        """
        cache_path = self._get_cache_path(key)
        meta_path = self._get_metadata_path(key)

        try:
            # Write data
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)

            # Write metadata
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'key': key
            }
            with open(meta_path, 'w') as f:
                json.dump(metadata, f)

        except Exception as e:
            print(f"Warning: Failed to write cache for {key}: {str(e)}")

    def clear(self, key: Optional[str] = None) -> None:
        """
        Clear cache.

        Args:
            key: Optional specific key to clear. If None, clears all cache.
        """
        if key:
            # Clear specific key
            cache_path = self._get_cache_path(key)
            meta_path = self._get_metadata_path(key)
            cache_path.unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)
        else:
            # Clear all cache
            for file in self.cache_dir.glob('*'):
                file.unlink()

    def get_size(self) -> int:
        """Get total cache size in bytes."""
        return sum(f.stat().st_size for f in self.cache_dir.glob('*'))

    def get_stats(self) -> dict:
        """Get cache statistics."""
        files = list(self.cache_dir.glob('*.pkl'))
        total_size = self.get_size()

        return {
            'num_items': len(files),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }


def cached(cache_key_fn: Callable[[Any], str], ttl_minutes: int = 15):
    """
    Decorator to cache function results.

    Args:
        cache_key_fn: Function to generate cache key from function arguments
        ttl_minutes: Time-to-live for cached data in minutes

    Example:
        @cached(lambda ticker, days: f"options_{ticker}_{days}", ttl_minutes=15)
        def get_options(ticker, days):
            # Expensive API call
            return fetch_data(ticker, days)
    """
    cache = DataCache(ttl_minutes=ttl_minutes)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_key_fn(*args, **kwargs)

            # Try to get from cache
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return cached_data

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)

            return result

        return wrapper

    return decorator


# Create global cache instance
_global_cache = DataCache()


def get_cache() -> DataCache:
    """Get global cache instance."""
    return _global_cache


def clear_cache(key: Optional[str] = None) -> None:
    """
    Clear global cache.

    Args:
        key: Optional specific key to clear. If None, clears all cache.
    """
    _global_cache.clear(key)


def get_cache_stats() -> dict:
    """Get global cache statistics."""
    return _global_cache.get_stats()

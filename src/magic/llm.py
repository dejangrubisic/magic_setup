"""Disk-cached Anthropic completions; safe to kill and rerun."""

from __future__ import annotations

import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor

import diskcache
from tqdm.auto import tqdm

DEFAULT_MODEL = "claude-sonnet-5"
DEFAULT_CACHE_DIR = "data/cache/llm"


def cache_key(
    prompt: str, model: str, system: str | None, max_tokens: int, temperature: float
) -> str:
    """Sha256 over the full request; any changed field is a different cache entry."""
    payload = {
        "model": model,
        "system": system,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def complete(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    system: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.0,
    cache_dir: str = DEFAULT_CACHE_DIR,
    client=None,
) -> str:
    """One cached completion; NO_CACHE=1 forces a fresh call but still writes the cache."""
    key = cache_key(prompt, model, system, max_tokens, temperature)
    with diskcache.Cache(str(cache_dir)) as cache:
        if os.environ.get("NO_CACHE") != "1":
            hit = cache.get(key)
            if hit is not None:
                return hit
        if client is None:
            import anthropic  # lazy: a key is only needed on a cache miss

            client = anthropic.Anthropic()
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system is not None:
            kwargs["system"] = system
        text = client.messages.create(**kwargs).content[0].text
        cache[key] = text
        return text


def complete_many(prompts: list[str], *, max_workers: int = 8, **kwargs) -> list[str]:
    """Thread-pool completions in input order; cached prompts return without an API call."""
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(complete, p, **kwargs) for p in prompts]
        return [f.result() for f in tqdm(futures, desc="llm", unit="req")]

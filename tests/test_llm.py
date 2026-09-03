from types import SimpleNamespace

import pytest

from magic.llm import cache_key, complete, complete_many


class FakeMessages:
    def __init__(self, calls):
        self.calls = calls

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            content=[SimpleNamespace(text=f"echo:{kwargs['messages'][0]['content']}")]
        )


class FakeClient:
    """Stand-in for anthropic.Anthropic: the network boundary, and the only fake here."""

    def __init__(self):
        self.calls = []
        self.messages = FakeMessages(self.calls)


@pytest.fixture
def client():
    return FakeClient()


def test_completion_is_cached_across_calls(tmp_path, client):
    first = complete("2+2?", cache_dir=tmp_path, client=client)
    second = complete("2+2?", cache_dir=tmp_path, client=client)
    assert first == second == "echo:2+2?"
    assert len(client.calls) == 1


def test_no_cache_env_forces_a_fresh_call(tmp_path, client, monkeypatch):
    complete("2+2?", cache_dir=tmp_path, client=client)
    monkeypatch.setenv("NO_CACHE", "1")
    assert complete("2+2?", cache_dir=tmp_path, client=client) == "echo:2+2?"
    assert len(client.calls) == 2
    monkeypatch.delenv("NO_CACHE")
    complete("2+2?", cache_dir=tmp_path, client=client)
    assert len(client.calls) == 2


@pytest.mark.parametrize(
    "kwargs",
    [
        {"prompt": "3+3?"},
        {"model": "claude-opus-5"},
        {"system": "be terse"},
        {"max_tokens": 8},
        {"temperature": 1.0},
    ],
)
def test_any_changed_field_is_a_cache_miss(tmp_path, client, kwargs):
    base = {"prompt": "2+2?", "model": "claude-sonnet-5", "system": None}
    complete(base.pop("prompt"), cache_dir=tmp_path, client=client, **base)
    merged = {**base, "prompt": "2+2?", **kwargs}
    complete(merged.pop("prompt"), cache_dir=tmp_path, client=client, **merged)
    assert len(client.calls) == 2


def test_request_passes_through_to_the_client(tmp_path, client):
    complete("hi", cache_dir=tmp_path, client=client, system="be terse", max_tokens=32)
    (call,) = client.calls
    assert call["model"] == "claude-sonnet-5"
    assert call["max_tokens"] == 32
    assert call["temperature"] == 0.0
    assert call["system"] == "be terse"
    assert call["messages"] == [{"role": "user", "content": "hi"}]


def test_system_omitted_when_none(tmp_path, client):
    complete("hi", cache_dir=tmp_path, client=client)
    assert "system" not in client.calls[0]


def test_cache_key_is_order_independent_but_content_sensitive():
    a = cache_key("p", "m", None, 10, 0.0)
    assert a == cache_key("p", "m", None, 10, 0.0)
    assert a != cache_key("p", "m", "s", 10, 0.0)
    assert len(a) == 64


def test_complete_many_preserves_order(tmp_path, client):
    prompts = [f"q{i}" for i in range(12)]
    out = complete_many(prompts, max_workers=4, cache_dir=tmp_path, client=client)
    assert out == [f"echo:q{i}" for i in range(12)]
    assert len(client.calls) == 12
    assert complete_many(prompts, max_workers=4, cache_dir=tmp_path, client=client) == out
    assert len(client.calls) == 12

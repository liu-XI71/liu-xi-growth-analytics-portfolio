from __future__ import annotations

from backend.config import Settings


def test_local_ollama_mode_requires_explicit_switch_and_accepts_local_endpoint() -> None:
    default = Settings(_env_file=None)
    assert default.copilot_narrative_mode == "deterministic"

    local = Settings(
        _env_file=None,
        copilot_narrative_mode="ollama",
        ollama_base_url="http://127.0.0.1:11434",
        ollama_model="local-test-model",
    )
    assert local.copilot_narrative_mode == "ollama"
    assert local.ollama_base_url == "http://127.0.0.1:11434"
    assert local.ollama_model == "local-test-model"

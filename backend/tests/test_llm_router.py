import pytest
from app.services.llm_router import llm_router


@pytest.mark.asyncio
async def test_llm_router_generation_and_fallback():
    prompt = "Explain repository architecture"
    system_prompt = "You are a code intelligence assistant"

    ans, provider, model, fb_occurred, chain = await llm_router.generate_response(
        prompt=prompt,
        system_prompt=system_prompt
    )

    assert isinstance(ans, str)
    assert len(ans) > 0
    assert provider in ("gemini", "groq", "nvidia", "openrouter", "openai", "mistral", "deepseek", "kimi", "ollama", "local_grounding")
    assert len(chain) > 0
    assert "status" in chain[-1]
    assert chain[-1]["status"] == "success"

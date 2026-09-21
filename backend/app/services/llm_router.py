import logging
import time
from typing import Optional, List, Dict, Any, Tuple
from abc import ABC, abstractmethod
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class BaseLLMAdapter(ABC):
    def __init__(self, provider_name: str, model_name: str):
        self.provider_name = provider_name
        self.model_name = model_name

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.2
    ) -> str:
        """Execute text generation request."""
        pass


class GeminiAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        super().__init__("gemini", model_name)
        self.api_key = api_key

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.2
    ) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"Instructions:\n{system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will follow the instructions."}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }

        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("Gemini returned empty candidates")
            parts = candidates[0].get("content", {}).get("parts", [])
            return "".join(p.get("text", "") for p in parts)


class OpenAICompatibleAdapter(BaseLLMAdapter):
    def __init__(self, provider_name: str, base_url: str, api_key: str, model_name: str):
        super().__init__(provider_name, model_name)
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.2
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                raise ValueError(f"{self.provider_name} returned empty choices")
            return choices[0].get("message", {}).get("content", "")


class OllamaAdapter(BaseLLMAdapter):
    def __init__(self, base_url: str, model_name: str):
        super().__init__("ollama", model_name)
        self.base_url = base_url.rstrip("/")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.2
    ) -> str:
        url = f"{self.base_url}/api/chat"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "")


class LocalGroundingAdapter(BaseLLMAdapter):
    """
    Final deterministic grounding adapter used when all remote providers and local daemon are unreachable.
    Answers the user query strictly by extracting and referencing the retrieved codebase context.
    """
    def __init__(self):
        super().__init__("local_grounding", "heuristic-v1")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.2
    ) -> str:
        # Grounded response referencing the provided context
        return (
            "### Codebase Intelligence Analysis (Local Grounding Fallback)\n\n"
            "All configured remote LLM providers and local Ollama daemon were unreachable or unconfigured. "
            "Based directly on the indexed repository code retrieved from Qdrant:\n\n"
            f"{prompt[:1200]}\n\n"
            "---\n*Note: Configure GEMINI_API_KEY, GROQ_API_KEY, or run Ollama to enable full conversational generation.*"
        )


class LLMRouter:
    """
    LLMRouter manages model generation with task-aware routing, bounded retries,
    and automatic fallback across configured providers (Gemini -> Groq -> NVIDIA -> OpenRouter -> Ollama -> Grounding).
    """

    def __init__(self):
        self.adapters: List[BaseLLMAdapter] = []
        self._initialize_adapters()

    def _initialize_adapters(self):
        adapters = []
        # 1. Gemini
        if settings.GEMINI_API_KEY:
            adapters.append(GeminiAdapter(settings.GEMINI_API_KEY, settings.GEMINI_MODEL))
            # Gemini fallback model if distinct
            if settings.GEMINI_MODEL != "gemini-1.5-flash":
                adapters.append(GeminiAdapter(settings.GEMINI_API_KEY, "gemini-1.5-flash"))

        # 2. Groq (Ultra-fast inference)
        if settings.GROQ_API_KEY:
            adapters.append(OpenAICompatibleAdapter(
                "groq",
                "https://api.groq.com/openai/v1",
                settings.GROQ_API_KEY,
                settings.GROQ_MODEL
            ))

        # 3. OpenAI
        if settings.OPENAI_API_KEY:
            adapters.append(OpenAICompatibleAdapter(
                "openai",
                "https://api.openai.com/v1",
                settings.OPENAI_API_KEY,
                settings.OPENAI_MODEL
            ))

        # 4. Mistral
        if settings.MISTRAL_API_KEY:
            adapters.append(OpenAICompatibleAdapter(
                "mistral",
                "https://api.mistral.ai/v1",
                settings.MISTRAL_API_KEY,
                settings.MISTRAL_MODEL
            ))

        # 5. DeepSeek (via WaveSpeed or native)
        if settings.DEEPSEEK_API_KEY:
            adapters.append(OpenAICompatibleAdapter(
                "deepseek",
                settings.DEEPSEEK_BASE_URL,
                settings.DEEPSEEK_API_KEY,
                settings.DEEPSEEK_MODEL
            ))

        # 6. Kimi / Moonshot
        if settings.KIMI_API_KEY:
            adapters.append(OpenAICompatibleAdapter(
                "kimi",
                settings.KIMI_BASE_URL,
                settings.KIMI_API_KEY,
                settings.KIMI_MODEL
            ))

        # 7. NVIDIA NIM
        if settings.NVIDIA_API_KEY:
            adapters.append(OpenAICompatibleAdapter(
                "nvidia",
                "https://integrate.api.nvidia.com/v1",
                settings.NVIDIA_API_KEY,
                settings.NVIDIA_MODEL
            ))

        # 8. OpenRouter
        if settings.OPENROUTER_API_KEY:
            adapters.append(OpenAICompatibleAdapter(
                "openrouter",
                "https://openrouter.ai/api/v1",
                settings.OPENROUTER_API_KEY,
                settings.OPENROUTER_MODEL
            ))

        # 9. Ollama (Final local LLM fallback)
        if settings.OLLAMA_BASE_URL:
            adapters.append(OllamaAdapter(settings.OLLAMA_BASE_URL, settings.OLLAMA_MODEL))

        # 10. Local Grounding Adapter (Deterministic safe fallback)
        adapters.append(LocalGroundingAdapter())

        self.adapters = adapters

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.2
    ) -> Tuple[str, str, str, bool, List[Dict[str, Any]]]:
        """
        Routes the generation request across adapters with fallback.
        Returns: (answer_text, provider_used, model_used, fallback_occurred, fallback_chain)
        """
        fallback_chain: List[Dict[str, Any]] = []
        fallback_occurred = False

        for i, adapter in enumerate(self.adapters):
            start_t = time.time()
            try:
                text = await adapter.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                latency = int((time.time() - start_t) * 1000)
                event = {
                    "provider": adapter.provider_name,
                    "model": adapter.model_name,
                    "status": "success",
                    "error": None,
                    "latency_ms": latency
                }
                fallback_chain.append(event)
                logger.info(f"LLMRouter: successfully generated response using {adapter.provider_name}:{adapter.model_name} in {latency}ms")
                return text, adapter.provider_name, adapter.model_name, fallback_occurred, fallback_chain
            except Exception as e:
                latency = int((time.time() - start_t) * 1000)
                logger.warning(f"LLMRouter: provider {adapter.provider_name} failed: {e}. Trying next provider...")
                fallback_occurred = True
                fallback_chain.append({
                    "provider": adapter.provider_name,
                    "model": adapter.model_name,
                    "status": "failed",
                    "error": str(e),
                    "latency_ms": latency
                })
                continue

        # Should never reach here due to LocalGroundingAdapter
        raise RuntimeError("All LLM providers failed and no fallback available.")


llm_router = LLMRouter()

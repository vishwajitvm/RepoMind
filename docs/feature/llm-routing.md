# Feature: Multi-Provider LLM Routing & Fallbacks

## Purpose
Enables robust, quota-aware LLM reasoning over code by dynamically cascading requests through verified model adapters.

## Architecture
- **Adapter Abstraction**: `BaseLLMAdapter` standardizes prompts, max tokens, and temperature across disparate APIs.
- **Provider Cascade**:
  1. `GeminiAdapter`: `gemini-1.5-flash`
  2. `GroqAdapter`: `llama-3.3-70b-versatile`
  3. `NvidiaAdapter`: `meta/llama-3.3-70b-instruct`
  4. `OpenRouterAdapter`: `meta-llama/llama-3.3-70b-instruct:free`
  5. `OllamaAdapter`: `deepseek-r1:1.5b` (Local fallback daemon)
  6. `LocalGroundingAdapter`: Heuristic grounded extractor (ultimate fallback)
- **Bounded Failover**: Failures (timeouts, 429 rate limits, 5xx errors) are intercepted, logged to the `fallback_chain` telemetry, and routed to the next adapter.

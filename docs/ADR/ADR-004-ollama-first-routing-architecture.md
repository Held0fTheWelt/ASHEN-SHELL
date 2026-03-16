# ADR-004: Ollama-First Routing Architecture

**Status:** Accepted

**Context:**

We are exploring ways to minimize inference costs while maintaining a good user experience. Currently, we're utilizing several LLM backends including Ollama, Claude Haiku, and Sonnet.  The cost differential is significant:

*   **Ollama:** $0 (Self-hosted, utilizing CPU)
*   **Claude Haiku:** $0.08 / 1M tokens
*   **Sonnet:** $3 / 1M tokens
*   **Opus:** $15 / 1M tokens

Our primary goal is to shift simpler tasks to Ollama (which is free) and only utilize more expensive models like Claude Sonnet for truly complex queries.  This allows us to drastically reduce our overall inference costs while still providing a viable fallback for complex requests.

**Decision:**

Route L0-L2 tasks to Ollama; L3-L4 to Claude API (Haiku & Sonnet); L5 stops and asks user for clarification.

**Escalation Matrix:**

This matrix defines the routing based on task complexity and model capabilities.

*   **L0 (trivial):** gemma3 (3.3GB, fast) - For the most basic prompts, we’ll use a lightweight model.
*   **L1 (simple):** gemma3 or qwen2.5-coder (33GB) - Simple tasks like basic question answering and text summarization.
*   **L2 (standard):** qwen2.5-coder or qwen3.5-35b (35GB) - Standard tasks including content generation and creative writing.
*   **L3 (complex):** Claude Haiku (fallback) - Tasks where Ollama’s capabilities are insufficient but Claude Haiku’s lower cost makes it preferable.
*   **L4 (very complex):** Claude Sonnet (fallback) -  Complex, nuanced tasks requiring substantial reasoning and knowledge.
*   **L5 (business decision):** Stop, ask user -  If the model cannot determine the user’s intent, we’ll halt processing and present the user with a prompt to clarify their request.  This is a safety net to avoid incorrect or nonsensical responses.

**Fallback Behavior:**

If Ollama is unavailable or fails to respond within a reasonable timeframe for L1/L2 tasks, the request will escalate to the Claude API (Haiku or Sonnet) unless the `force_ollama` flag is set to `True`. The `force_ollama` flag would only be used in controlled environments for testing or debugging.

**Consequences:**

*   **90%+ cost savings:** By prioritizing Ollama for simpler tasks, we anticipate a significant reduction in inference costs.
*   **Latency tradeoff for CPU-based 70b models:** Shifting to Ollama’s CPU-based models will introduce a latency tradeoff compared to the faster GPU models.  This is an acceptable tradeoff for the substantial cost savings.

**Alternatives Considered:**

*   **Claude-only:**  Routing all requests to Claude would be simpler to implement but would significantly increase inference costs.
*   **Random routing:** Randomly assigning models could lead to inefficient resource utilization and potentially poor performance.
*   **Capability-based routing:**  Similar to this approach, but defining capabilities would require significant manual effort and ongoing maintenance.

---
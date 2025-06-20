# Future Update Doc - Specialized LLM Models for Agents**

The "AI Rails" system leverages a hybrid LLM strategy, prioritizing powerful, specialized self-hosted models running on your AI Workhorse (RTX 5090) for most tasks, with strategic use of cloud APIs for exceptional cases. This approach balances performance, cost, precision, and data sovereignty.

## **Model Allocation Strategy:**

Each agent is paired with models optimized for its specific task, considering factors like reasoning ability, code generation quality, context window, speed, and VRAM requirements.

| Agent Role              | Primary Self-Hosted Recommendation        | Justification & VRAM Considerations (RTX 5090)                                                                                                              | Cloud Fallback (for extreme cases) |
| :---------------------- | :---------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------- |
| **Planning Agent** | `WizardLM-2-8x22B-GGUF (Q4_K_M)`          | Superior complex reasoning, beats GPT-4 on planning benchmarks; runs at ~25GB VRAM with llama.cpp quantization.                                               | `Claude 4 Opus`                  |
| **Coder Agent** | `DeepSeek-Coder-33B-Instruct`             | Purpose-built for code generation, trained on 2T tokens; fits at full precision (32GB VRAM); outperforms GPT-3.5.                                            | -                                |
| **Unit Tester Agent** | `StarCoder2-15B-Instruct-v0.1`            | Fine-tuned specifically on test generation; understands pytest/unittest patterns; ~15GB VRAM.                                                                 | -                                |
| **Debugger Agent** | `WizardCoder-33B-V1.1`                    | Exceptional at understanding error messages; fine-tuned on debugging conversations for superior root cause analysis.                                        | -                                |
| **Documentation Agent** | `OpenHermes-2.5-Mistral-7B`               | Excellent natural writing style, avoids "AI-speak," fine-tuned on high-quality text; leaves ample VRAM.                                                     | -                                |
| **Code Review Agent** | `CodeLlama-34B-Instruct`                  | Native understanding of code patterns; excellent with Semgrep rules for security; can load security-focused LoRAs. (Consider pre-processing with `SecBERT`). | -                                |
| **Refactor Agent** | `Refact-1.6B`                             | Purpose-built for refactoring by SmallCloudAI; very tiny model with high performance; multiple instances can run.                                           | -                                |
| **n8n Flow Creator Agent**| `Mistral-7B-OpenOrca`                     | Excels at JSON generation; fine-tuned on structured data for consistent output.                                                                               | -                                |
| **Overseer Agent** | `TinyLlama-1.1B` (multiple instances)     | Allows running many specialized instances for different log patterns; fine-tunable on specific logs for targeted anomaly detection.                          | -                                |

## **Overall Model Strategy:**

* **Local-First:** Maximizes your RTX 5090, eliminating API costs and enhancing privacy/security.
* **Specialization:** Chooses models fine-tuned for specific agent tasks to maximize precision and performance.
* **Quantization:** Utilizes optimal quantization (e.g., Q4_K_M for 70B, FP16 for 34B if it fits) to balance quality and VRAM usage.
* **Hybrid Approach:** `Claude 4 Opus` is retained as a strategic cloud fallback for the Planning Agent for the most complex architectural challenges, leveraging its exceptional reasoning when local resources or models might struggle.
* **Flexible Deployment:** Models can be managed via Ollama for ease of use or `llama.cpp`/`vLLM` for maximum control and performance.

---
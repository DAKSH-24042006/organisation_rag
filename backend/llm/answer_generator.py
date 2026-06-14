"""
Answer generation with a local Ollama model.

Recommended local models (pull with `ollama pull <name>`):
  - embeddings: nomic-embed-text   (768-dim, 8192-token context)
  - generation: qwen2.5-coder:7b   (or :32b on a bigger GPU)
  - debugging : deepseek-r1:32b    (step-by-step bug reasoning, optional)
"""

from __future__ import annotations

import ollama
from rag.config import OLLAMA_MODEL


class OllamaAnswerer:
    """Sends a retrieved-context prompt to a local Ollama generation model."""

    def __init__(self, model: str = OLLAMA_MODEL) -> None:
        """
        Args:
            model: Ollama model tag used for generation. Swap per query type if
                you want (e.g. deepseek-r1 for 'dfs' debug queries).
        """
        self.model = model

    def answer(self, query: str, context: str) -> str:
        """
        Generate an answer for a query and its retrieved context.

        Returns the model's text response. Requires the `ollama` Python package
        and a running Ollama server (`ollama serve`).
        """
        from rag.retriever import classify_query
        qtype = classify_query(query)

        if qtype == "FILE_RECOVERY":
            prompt = f"""You are a software repository assistant.
The user is requesting the full code of a file.

Below is the retrieved full content of the file. Please present the complete, uninterrupted code inside a single Markdown code block, with correct syntax highlighting. Do not explain, truncate, summarize, or omit any parts of the code.

File Content:
{context}

Answer:
"""
        elif qtype == "OVERVIEW":
            prompt = f"""You are an expert software architect assistant.
The user is requesting a high-level overview or architectural understanding of the codebase.

Review the retrieved Repository Architecture Map and README files in the Context Package below. Provide a clear, structured, and comprehensive explanation of the system's purpose, technology stack, directory layout, major modules, service APIs, and database structures.

DO NOT hallucinate folders, routes, or files that are not explicitly documented in the retrieved package. Frame your response clearly under separate markdown headings.

Question:
{query}

Retrieved Context Package:
{context}

Answer (Structured & Architectural):
"""
        elif qtype == "DEBUG":
            prompt = f"""You are a senior system debugger and diagnostics assistant.
The user is troubleshooting a bug, traceback error, or failure in the codebase.

Analyze the Context Package below, which contains caller-callee active call dependency graphs and code evidence segments. Identify the root cause of the error (e.g., token verification, connection timeout, validate exceptions) by tracing the execution path from callers (like API middleware or controllers) down to the target functions.

Cite exact file names and line ranges when detailing the execution cascade.

Question:
{query}

Retrieved Context Package:
{context}

Diagnostic Answer (Root-Cause Trace & Code Citations):
"""
        else:  # CODE_SEARCH
            prompt = f"""You are a helpful software repository assistant.
The user is looking for specific functionality, classes, functions, or implementing a new feature.

Answer the user's question precisely using only the provided code evidence in the retrieved Context Package. Present clear explanation, cite the relevant files and line numbers, and provide code blocks where helpful.

If the functionality cannot be found in the context, say so clearly.

Question:
{query}

Retrieved Context Package:
{context}

Answer (Precise & Evidence-backed):
"""

        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={
                "num_ctx":     9000,
                "num_predict": 2048,
                "temperature": 0.2,
            },
        )
        return response["message"]["content"]

    def answer_query(self, retriever, query: str, **kwargs) -> str:
        """
        Convenience: retrieve for `query` then generate an answer in one call.

        Args:
            retriever: a Retriever instance.
            query: the user's question.
            **kwargs: passed through to retriever.retrieve (top_k, depth, ...).

        Returns:
            answer_text
        """
        context = retriever.retrieve(query, **kwargs)
        return self.answer(query, context)


# Module-level convenience function for backward compatibility
def generate_answer(query: str, context: str) -> str:
    return OllamaAnswerer().answer(query, context)
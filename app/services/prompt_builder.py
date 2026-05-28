from app.schemas.qa import RetrievedChunk

# 负责“整理汇报材料”，并对其加上严格的指令，最终一起提交给大模型（如 OpenAI 或本地的开源大模型）。
class PromptBuilder:
    def build_rag_prompt(
        self,
        query: str,
        retrieved_chunks: list[RetrievedChunk],
    ) -> str:
        context_parts: list[str] = []

        for index, chunk in enumerate(retrieved_chunks, start=1):
            source_name = chunk.metadata.get("original_filename", "unknown source")

            context_parts.append(
                f"[Source {index}: {source_name}]\n{chunk.content}"
            )

        context = "\n\n".join(context_parts)

        return f"""You are an enterprise knowledge base assistant.

Answer the user's question based only on the provided context.
If the context does not contain the answer, say you don't know.
Keep the answer concise and factual.

Context:
{context}

Question:
{query}

Answer:
"""
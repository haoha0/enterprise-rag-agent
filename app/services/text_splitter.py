from app.schemas.chunk import TextChunk


class TextSplitter:
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0.")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must be greater than or equal to 0.")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(
        self,
        text: str,
        document_id: str,
        metadata: dict | None = None,
    ) -> list[TextChunk]:
        cleaned_text = text.strip()

        if not cleaned_text:
            return []

        metadata = metadata or {}
        chunks: list[TextChunk] = []

        start = 0
        chunk_index = 0
        text_length = len(cleaned_text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            content = cleaned_text[start:end].strip()

            if content:
                chunk_id = f"{document_id}_chunk_{chunk_index}"

                chunks.append(
                    TextChunk(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        chunk_index=chunk_index,
                        content=content,
                        content_length=len(content),
                        metadata={
                            **metadata,
                            "start_char": start,
                            "end_char": end,
                        },
                    )
                )

                chunk_index += 1

            start += self.chunk_size - self.chunk_overlap

        return chunks
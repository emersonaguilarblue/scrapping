class Chunker:
    def __init__(self, chunk_size: int, overlap: int) -> None:
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        chunks: list[str] = []
        start = 0
        length = len(text)

        while start < length:
            end = min(start + self.chunk_size, length)
            chunk = text[start:end]
            boundary = self._find_boundary(chunk)
            if boundary and end < length:
                chunk = chunk[:boundary]
                end = start + boundary
            chunks.append(chunk.strip())
            if end >= length:
                break
            start = max(end - self.overlap, start + 1)

        return [c for c in chunks if c]

    @staticmethod
    def _find_boundary(chunk: str) -> int:
        for sep in ("\n\n", ". ", "\n", " "):
            idx = chunk.rfind(sep)
            if idx > len(chunk) * 0.5:
                return idx + len(sep)
        return 0

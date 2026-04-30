from pathlib import Path

import pandas as pd
from loguru import logger
from slugify import slugify

from src.core.exceptions import StorageError
from src.core.models import ScrapedDocument


class PklStore:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.markdown_dir = output_dir / "markdown"
        self.markdown_dir.mkdir(parents=True, exist_ok=True)

    def export(self, documents: list[ScrapedDocument]) -> dict[str, Path]:
        if not documents:
            raise StorageError("No documents to export")

        rows_flat = []
        rows_chunks = []
        md_files: list[Path] = []

        for doc in documents:
            md_text = doc.markdown or doc.content
            md_path = self.markdown_dir / f"{slugify(doc.source_id)}.md"
            md_path.write_text(md_text, encoding="utf-8")
            md_files.append(md_path)

            base = {
                "source_id": doc.source_id,
                "url": str(doc.url),
                "title": doc.title,
                "content": doc.content,
                "markdown": doc.markdown,
                "content_hash": doc.content_hash,
                "scraped_at": doc.scraped_at,
                "category": doc.metadata.get("category"),
                "strategy": doc.metadata.get("strategy"),
                "breadcrumb": doc.metadata.get("breadcrumb"),
                "content_length": doc.metadata.get("content_length", len(doc.content)),
                "markdown_length": doc.metadata.get("markdown_length", len(doc.markdown)),
                "num_chunks": len(doc.chunks),
            }
            rows_flat.append(base)

            for i, chunk in enumerate(doc.chunks):
                rows_chunks.append(
                    {
                        "source_id": doc.source_id,
                        "chunk_index": i,
                        "chunk_text": chunk,
                        "chunk_length": len(chunk),
                        "category": doc.metadata.get("category"),
                        "url": str(doc.url),
                        "content_hash": doc.content_hash,
                    }
                )

        df_docs = pd.DataFrame(rows_flat)
        df_chunks = pd.DataFrame(rows_chunks)

        saved: dict[str, Path] = {}

        path_docs = self.output_dir / "documents.pkl"
        df_docs.to_pickle(path_docs)
        saved["documents"] = path_docs
        logger.info(f"exported {len(df_docs)} docs -> {path_docs.name}")

        path_chunks = self.output_dir / "chunks.pkl"
        df_chunks.to_pickle(path_chunks)
        saved["chunks"] = path_chunks
        logger.info(f"exported {len(df_chunks)} chunks -> {path_chunks.name}")

        for category, group in df_docs.groupby("category"):
            safe = str(category).replace(" ", "_")
            path = self.output_dir / f"docs_{safe}.pkl"
            group.reset_index(drop=True).to_pickle(path)
            saved[f"docs_{safe}"] = path
            logger.info(f"  partition [{category}] {len(group)} docs -> {path.name}")

        for category, group in df_chunks.groupby("category"):
            safe = str(category).replace(" ", "_")
            path = self.output_dir / f"chunks_{safe}.pkl"
            group.reset_index(drop=True).to_pickle(path)
            saved[f"chunks_{safe}"] = path

        path_xlsx = self.output_dir / "documents.xlsx"
        with pd.ExcelWriter(path_xlsx, engine="openpyxl") as writer:
            summary_cols = ["source_id", "title", "breadcrumb", "category", "strategy", "content_length", "num_chunks", "scraped_at"]
            df_docs[summary_cols].to_excel(writer, sheet_name="resumen", index=False)

            for _, row in df_docs.iterrows():
                sid = str(row["source_id"])
                doc_chunks = df_chunks[df_chunks["source_id"] == sid][["chunk_index", "chunk_text", "chunk_length"]].reset_index(drop=True)
                sheet_name = sid[:31]  # Excel max 31 chars
                doc_chunks.to_excel(writer, sheet_name=sheet_name, index=False)

        saved["xlsx"] = path_xlsx
        logger.info(f"exported xlsx ({len(df_docs)} sheets) -> {path_xlsx.name}")
        logger.info(f"exported {len(md_files)} markdown files -> {self.markdown_dir.name}/")

        return saved

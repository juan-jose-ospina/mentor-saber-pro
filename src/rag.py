# =============================================================================
# src/rag.py – Pipeline RAG completo (Ingesta · Chunking · ChromaDB · Nomic)
# =============================================================================

import glob
from pathlib import Path
from typing import List

import streamlit as st

# ── Rutas ─────────────────────────────────────────────────────────────────────
_BASE_DIR   = Path(__file__).resolve().parent.parent
DATA_DIR    = _BASE_DIR / "data"
CHROMA_DIR  = str(_BASE_DIR / "chroma_db")

# ── Hiperparámetros RAG ───────────────────────────────────────────────────────
CHUNK_SIZE    = 512
CHUNK_OVERLAP = 64
TOP_K         = 4
COLLECTION    = "icfes_corpus"


# ─────────────────────────────────────────────────────────────────────────────
# Embeddings (cacheados en proceso para no reinicializar el modelo)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="🔄 Cargando modelo de embeddings…")
def get_embeddings():
    """Inicializa nomic-embed-text-v1.5 vía sentence-transformers. FR2 / SRS §2.1."""
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(
        model_name="nomic-ai/nomic-embed-text-v1.5",
        model_kwargs={"trust_remote_code": True},
        encode_kwargs={"normalize_embeddings": True},
    )


# ─────────────────────────────────────────────────────────────────────────────
# VectorStore
# ─────────────────────────────────────────────────────────────────────────────

def _get_vectorstore(embeddings):
    """Devuelve la instancia de ChromaDB persistida. FR2.3."""
    from langchain_chroma import Chroma

    return Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Ingesta
# ─────────────────────────────────────────────────────────────────────────────

def ingest_pdfs(embeddings) -> str:
    """
    Lee todos los PDFs de /data con PyMuPDF, divide en chunks recursivos y los
    indexa en ChromaDB. FR2.1 · FR2.2 · FR2.3 · FR4.1.

    Retorna un mensaje de estado para mostrar en la UI.
    """
    import fitz  # PyMuPDF
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_chroma import Chroma
    from langchain_core.documents import Document

    pdf_files: List[str] = glob.glob(str(DATA_DIR / "*.pdf"))
    if not pdf_files:
        return "⚠️ No se encontraron PDFs en la carpeta `data/`."

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    all_docs: List[Document] = []
    for pdf_path in pdf_files:
        source_name = Path(pdf_path).name
        try:
            doc_pdf = fitz.open(pdf_path)
            full_text = "".join(page.get_text() for page in doc_pdf)
            doc_pdf.close()

            for chunk in splitter.split_text(full_text):
                all_docs.append(
                    Document(
                        page_content=chunk,
                        metadata={"source": source_name},
                    )
                )
        except Exception as exc:
            st.warning(f"Error leyendo {source_name}: {exc}")

    if not all_docs:
        return "⚠️ Los PDFs no contienen texto extraíble."

    Chroma.from_documents(
        documents=all_docs,
        embedding=embeddings,
        collection_name=COLLECTION,
        persist_directory=CHROMA_DIR,
    )
    return f"✅ Indexados {len(all_docs)} fragmentos de {len(pdf_files)} PDF(s)."


# ─────────────────────────────────────────────────────────────────────────────
# Recuperación con Cross-Encoder re-ranking opcional
# ─────────────────────────────────────────────────────────────────────────────

def retrieve_context(query: str, embeddings) -> str:
    """
    Recupera los TOP_K fragmentos más relevantes del corpus ICFES. FR2.4.
    Aplica Cross-Encoder re-ranking si sentence-transformers está disponible;
    en caso contrario usa similitud vectorial directa como fallback.
    """
    vectorstore = _get_vectorstore(embeddings)
    results = vectorstore.similarity_search(query, k=TOP_K * 2)

    if not results:
        return "No se encontró información relevante en el corpus ICFES."

    try:
        from sentence_transformers import CrossEncoder

        ce = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        pairs = [(query, doc.page_content) for doc in results]
        scores = ce.predict(pairs)
        ranked = sorted(zip(scores, results), key=lambda x: x[0], reverse=True)
        results = [doc for _, doc in ranked[:TOP_K]]
    except Exception:
        results = results[:TOP_K]

    context_parts = [
        f"[Fuente: {doc.metadata.get('source', 'desconocido')}]\n{doc.page_content}"
        for doc in results
    ]
    return "\n\n---\n\n".join(context_parts)

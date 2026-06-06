# =============================================================================
# src/app.py – Punto de entrada Streamlit (Frontend único)
# Stack: Streamlit · LangGraph · Gemini 3.5 Flash · ChromaDB · PyMuPDF · ReportLab
# =============================================================================

import os
import glob
from pathlib import Path

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

# ── Primera llamada Streamlit (obligatoria antes de cualquier otra) ────────────
st.set_page_config(
    page_title="Mentor Saber Pro – ICFES",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Módulos locales ────────────────────────────────────────────────────────────
from state import AgentState
from rag import get_embeddings, ingest_pdfs, retrieve_context, DATA_DIR
from skills import generate_pdf_report
from agents import build_graph

# =============================================================================
# CSS – PALETA OFICIAL ICFES
# =============================================================================

def _inject_css() -> None:
    """Inyecta la hoja de estilos con la identidad visual institucional del ICFES."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* ── Tipografía global ── */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* ── Fondo principal: blanco/gris claro ── */
        .stApp {
            background-color: #F4F6F9;
            min-height: 100vh;
        }

        /* ── Sidebar: Azul Oscuro Institucional ICFES ── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #002B49 0%, #0F2C59 100%);
            border-right: 3px solid #FFCD00;
        }
        section[data-testid="stSidebar"] * {
            color: #E8EAF6 !important;
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #FFCD00 !important;
        }
        section[data-testid="stSidebar"] .stCaption,
        section[data-testid="stSidebar"] p {
            color: #B0BEC5 !important;
        }

        /* ── Botones de acción: Amarillo/Oro ICFES ── */
        .stButton > button {
            background: linear-gradient(135deg, #FFCD00 0%, #F9A825 100%);
            color: #002B49 !important;
            border: none;
            border-radius: 10px;
            padding: 0.55rem 1.1rem;
            font-weight: 700;
            font-size: 0.92rem;
            letter-spacing: 0.01em;
            transition: all 0.25s ease;
            width: 100%;
            box-shadow: 0 2px 8px rgba(255, 205, 0, 0.35);
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(255, 205, 0, 0.55);
            background: linear-gradient(135deg, #FFE033 0%, #FFCD00 100%);
        }
        .stButton > button:active {
            transform: translateY(0);
        }

        /* ── Download button: mismo estilo ── */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #FFCD00 0%, #F9A825 100%);
            color: #002B49 !important;
            border: none;
            border-radius: 10px;
            padding: 0.55rem 1.1rem;
            font-weight: 700;
            width: 100%;
            box-shadow: 0 2px 8px rgba(255, 205, 0, 0.35);
            transition: all 0.25s ease;
        }
        .stDownloadButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(255, 205, 0, 0.55);
        }

        /* ── Encabezado principal ── */
        .mentor-header {
            background: linear-gradient(135deg, #002B49 0%, #0F2C59 80%, #1565C0 100%);
            border-radius: 18px;
            padding: 2rem 2.5rem 1.6rem;
            margin-bottom: 1.5rem;
            border-left: 6px solid #FFCD00;
            box-shadow: 0 4px 24px rgba(0, 43, 73, 0.18);
        }
        .mentor-header h1 {
            color: #FFFFFF !important;
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            margin: 0 0 0.3rem !important;
            letter-spacing: -0.5px;
        }
        .mentor-header p {
            color: #B0C4D8 !important;
            font-size: 1rem !important;
            margin: 0 !important;
        }
        .mentor-header .badge {
            display: inline-block;
            background: #FFCD00;
            color: #002B49;
            font-size: 0.72rem;
            font-weight: 700;
            border-radius: 20px;
            padding: 2px 10px;
            margin-top: 0.6rem;
            letter-spacing: 0.04em;
        }

        /* ── Burbujas de chat ── */
        [data-testid="stChatMessage"] {
            border-radius: 16px;
            margin-bottom: 10px;
            border: 1px solid rgba(0, 43, 73, 0.08);
            background: #FFFFFF;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            padding: 4px 8px;
        }
        [data-testid="stChatMessage"][data-testid*="user"] {
            background: #EEF5FB;
        }

        /* ── Input de chat ── */
        .stChatInputContainer {
            background: #FFFFFF;
            border-radius: 14px;
            border: 2px solid #0F2C59;
            box-shadow: 0 2px 10px rgba(15, 44, 89, 0.10);
        }
        .stChatInputContainer:focus-within {
            border-color: #FFCD00;
            box-shadow: 0 2px 14px rgba(255, 205, 0, 0.25);
        }

        /* ── Score cards ── */
        .score-card {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 205, 0, 0.3);
            border-radius: 12px;
            padding: 12px 8px;
            text-align: center;
            margin: 4px 0;
        }
        .score-number {
            font-size: 2rem;
            font-weight: 700;
            line-height: 1;
        }
        .score-label {
            font-size: 0.72rem;
            opacity: 0.75;
            margin-top: 5px;
        }

        /* ── Alertas / st.warning, st.info ── */
        div[data-testid="stAlert"] {
            border-radius: 12px;
        }

        /* ── Progress bar ── */
        .stProgress > div > div {
            background: linear-gradient(90deg, #FFCD00, #F9A825);
            border-radius: 4px;
        }

        /* ── Separadores sidebar ── */
        hr { border-color: rgba(255, 205, 0, 0.25) !important; }

        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #F4F6F9; }
        ::-webkit-scrollbar-thumb { background: #0F2C59; border-radius: 3px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# SESSION STATE
# =============================================================================

def _init_session_state() -> None:
    """Inicializa las variables de sesión de Streamlit con sus valores por defecto."""
    defaults: dict = {
        "messages":        [],   # [{role, content}] para renderizar el chat
        "agent_messages":  [],   # [BaseMessage] para el grafo LangGraph
        "score_correct":   0,
        "score_incorrect": 0,
        "api_key_set":     False,
        "graph":           None,
        "embeddings":      None,
        "ingested":        False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# =============================================================================
# SIDEBAR
# =============================================================================

def _render_sidebar() -> None:
    """Renderiza la barra lateral con controles y métricas. FR3.2."""
    with st.sidebar:
        # ── Logo / título ─────────────────────────────────────────────────────
        st.markdown(
            """
            <div style='text-align:center; padding: 1.2rem 0 0.8rem;'>
                <span style='font-size:3rem;'>🎓</span><br>
                <span style='font-size:1.25rem; font-weight:700; color:#FFCD00;'>
                    Mentor Saber Pro
                </span><br>
                <span style='font-size:0.74rem; color:#90A4AE; letter-spacing:0.06em;'>
                    ASISTENTE ICFES &nbsp;·&nbsp; v2.0
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # ── API Key (NFR2 / NFR4) ─────────────────────────────────────────────
        st.markdown("### 🔑 API Key de Google")
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIza…",
            label_visibility="collapsed",
            key="api_key_input",
        )
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
            st.session_state["api_key_set"] = True
            st.success("✅ API Key configurada", icon="🔓")
        else:
            st.session_state["api_key_set"] = False

        st.markdown("---")

        # ── Puntaje de la sesión (FR3.2.b) ────────────────────────────────────
        st.markdown("### 📊 Puntaje de la Sesión")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"""
                <div class='score-card'>
                    <div class='score-number' style='color:#66BB6A;'>
                        {st.session_state['score_correct']}
                    </div>
                    <div class='score-label'>Correctas ✅</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""
                <div class='score-card'>
                    <div class='score-number' style='color:#EF5350;'>
                        {st.session_state['score_incorrect']}
                    </div>
                    <div class='score-label'>Incorrectas ❌</div>
                </div>""",
                unsafe_allow_html=True,
            )

        total = st.session_state["score_correct"] + st.session_state["score_incorrect"]
        if total > 0:
            pct = st.session_state["score_correct"] / total * 100
            st.progress(int(pct), text=f"Efectividad: {pct:.0f}%")

        st.markdown("---")

        # ── Corpus ICFES (FR3.2.c / FR4.1) ───────────────────────────────────
        st.markdown("### 📂 Corpus ICFES")
        pdf_count = len(glob.glob(str(DATA_DIR / "*.pdf")))
        st.caption(f"PDFs detectados en /data: **{pdf_count}**")

        if st.button("🔄 Indexar PDFs ahora", use_container_width=True, key="btn_index"):
            if st.session_state["embeddings"] is None:
                st.session_state["embeddings"] = get_embeddings()
            with st.spinner("Indexando corpus…"):
                msg = ingest_pdfs(st.session_state["embeddings"])
            st.info(msg)
            st.session_state["ingested"] = True

        if st.session_state["ingested"]:
            st.caption("✅ Corpus indexado y listo")

        st.markdown("---")

        # ── Reporte PDF (FR3.2.d / FR4.2) ────────────────────────────────────
        st.markdown("### 📄 Reporte de Desempeño")
        if st.button("📥 Generar Reporte PDF", use_container_width=True, key="btn_report"):
            pdf_bytes = generate_pdf_report(
                st.session_state["score_correct"],
                st.session_state["score_incorrect"],
            )
            st.download_button(
                label="⬇️ Descargar Reporte",
                data=pdf_bytes,
                file_name="reporte_desempeno_icfes.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="btn_download",
            )

        st.markdown("---")

        # ── Instrucciones rápidas ─────────────────────────────────────────────
        st.markdown(
            """
            <div style='font-size:0.78rem; color:#90A4AE; line-height:1.8;'>
            <b style='color:#FFCD00;'>💡 ¿Cómo usar?</b><br>
            • Pregunta sobre teoría → <b>Agente Profesor</b><br>
            • Pide un quiz o simulacro → <b>Agente Evaluador</b><br>
            • Responde <b>A, B, C o D</b> para ser calificado<br>
            • Indexa los PDFs del ICFES antes de chatear
            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================================
# GRAPH MANAGEMENT
# =============================================================================

def _get_or_build_graph():
    """
    Crea (o reutiliza desde session_state) el grafo LangGraph.
    Retorna None si la API Key no está configurada aún. NFR2.
    """
    if st.session_state["graph"] is not None:
        return st.session_state["graph"]

    if not st.session_state["api_key_set"]:
        return None

    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0.3,
        max_retries=3,
    )

    if st.session_state["embeddings"] is None:
        st.session_state["embeddings"] = get_embeddings()

    st.session_state["graph"] = build_graph(llm, st.session_state["embeddings"])
    return st.session_state["graph"]


def _extract_clean_text(content) -> str:
    """Extrae exclusivamente el valor del texto limpio de la respuesta del LLM."""
    if isinstance(content, list):
        if len(content) > 0:
            first = content[0]
            if isinstance(first, dict):
                return str(first.get("text", first))
            return str(first)
        return ""
    elif isinstance(content, dict):
        return str(content.get("text", content))
    return str(content)


def _run_graph(user_input: str) -> str | None:
    """
    Ejecuta el grafo LangGraph con el mensaje del usuario y actualiza el estado
    de Streamlit con la respuesta del agente y los puntajes. FR3.1.
    """
    graph = _get_or_build_graph()
    if graph is None:
        return None

    current_state: AgentState = {
        "messages":        st.session_state["agent_messages"] + [HumanMessage(content=user_input)],
        "intent":          "",
        "score_correct":   st.session_state["score_correct"],
        "score_incorrect": st.session_state["score_incorrect"],
    }

    result: AgentState = graph.invoke(current_state)

    st.session_state["agent_messages"]  = result["messages"]
    st.session_state["score_correct"]   = result["score_correct"]
    st.session_state["score_incorrect"] = result["score_incorrect"]

    last_ai = next(
        (m for m in reversed(result["messages"]) if isinstance(m, AIMessage)),
        None,
    )
    if last_ai:
        return _extract_clean_text(last_ai.content)
    return "Sin respuesta del agente."


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    """Punto de entrada principal de la aplicación Streamlit."""
    _inject_css()
    _init_session_state()
    _render_sidebar()

    # ── Encabezado principal con identidad ICFES ──────────────────────────────
    st.markdown(
        """
        <div class='mentor-header'>
            <h1>🎓 Mentor Saber Pro</h1>
            <p>Asistente Inteligente para la Preparación de Pruebas ICFES / Saber Pro</p>
            <span class='badge'>✦ POWERED BY GEMINI 3.5 FLASH + RAG</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Advertencia sin API Key (NFR2) ────────────────────────────────────────
    if not st.session_state["api_key_set"]:
        st.warning(
            "⚠️ **API Key requerida.** Ingresa tu Gemini API Key en el panel "
            "lateral izquierdo para activar los agentes de IA.",
            icon="🔑",
        )

    # ── Historial de chat (FR3.1) ─────────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        if not st.session_state["messages"]:
            with st.chat_message("assistant", avatar="🎓"):
                st.markdown(
                    """
¡Hola! Soy tu **Mentor Saber Pro** 🎓

Cuento con dos agentes especializados:

- 📚 **Agente Profesor** → Explica conceptos, definiciones y tips para el examen.
- 📝 **Agente Evaluador** → Formula preguntas tipo ICFES y califica tus respuestas.

**Para empezar:**
1. Ingresa tu API Key de Google Gemini en el panel lateral.
2. Indexa los PDFs del ICFES desde el panel lateral.
3. ¡Escribe tu primera pregunta o pide un simulacro!
                    """
                )

        for msg in st.session_state["messages"]:
            avatar = "🧑‍🎓" if msg["role"] == "user" else "🎓"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # ── Input del usuario (FR3.1) ─────────────────────────────────────────────
    user_input = st.chat_input(
        "Escribe tu pregunta o pide un simulacro…",
        disabled=not st.session_state["api_key_set"],
    )

    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner("🤔 Pensando…"):
                response = _run_graph(user_input)

            if response:
                st.markdown(response)
                st.session_state["messages"].append(
                    {"role": "assistant", "content": response}
                )
            else:
                st.error(
                    "❌ No se pudo obtener respuesta. "
                    "Verifica la API Key y que los PDFs estén indexados."
                )

        st.rerun()


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================
if __name__ == "__main__":
    main()
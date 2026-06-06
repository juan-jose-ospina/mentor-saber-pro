# =============================================================================
# src/state.py – Definición fuertemente tipada del estado de LangGraph
# =============================================================================

from typing import List
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Estado global del grafo LangGraph. FR1.2 / SRS §2.2."""

    messages: List[BaseMessage]
    """Historial completo de mensajes del diálogo."""

    intent: str
    """Intención clasificada por el Router: 'PROFESOR' | 'EVALUADOR' | ''."""

    score_correct: int
    """Contador acumulado de respuestas correctas en la sesión."""

    score_incorrect: int
    """Contador acumulado de respuestas incorrectas en la sesión."""

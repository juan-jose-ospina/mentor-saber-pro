# =============================================================================
# src/agents.py – Prompts, nodos LangGraph y grafo compilado (FR §2.2)
# =============================================================================

from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from state import AgentState
from rag import retrieve_context

import re
from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

# =============================================================================
# PROMPTS DEL SISTEMA (SRS §2.2)
# =============================================================================

ROUTER_PROMPT = """Eres un clasificador de intenciones educativas. Analiza el \
mensaje del usuario y responde ÚNICAMENTE con una de estas dos palabras:
- PROFESOR  → si el usuario pide teoría, definiciones, explicaciones o ejemplos.
- EVALUADOR → si el usuario pide un simulacro, quiz, pregunta de práctica o \
está respondiendo con A, B, C o D.

Mensaje del usuario: {message}
Respuesta (una sola palabra):"""

PROFESOR_PROMPT = """Eres el Agente Profesor del sistema Mentor Saber Pro, un \
experto pedagógico en las Pruebas de Estado ICFES/Saber Pro de Colombia.

CONTEXTO RECUPERADO DEL CORPUS ICFES:
{context}

Responde la siguiente pregunta estructurando tu respuesta OBLIGATORIAMENTE en \
cuatro partes claramente numeradas:
1. **Definición:** Explica el concepto de forma clara y precisa.
2. **Ejemplo práctico:** Ilustra con un caso concreto del contexto ICFES.
3. **Tip para el examen:** Da una estrategia o truco mnemotécnico para el día \
del examen.
4. **Fuente consultada:** Indica el nombre del PDF del corpus del que proviene \
la información.

Pregunta del estudiante: {question}"""

EVALUADOR_PROMPT = """Eres el Agente Evaluador del sistema Mentor Saber Pro. \
Tu función es formular preguntas tipo ICFES y calificar las respuestas.

CONTEXTO RECUPERADO DEL CORPUS ICFES:
{context}

Historial de la conversación reciente:
{history}

Mensaje actual del usuario: {message}

Si el usuario está pidiendo un simulacro o quiz:
- Formula UNA pregunta de opción múltiple con 4 opciones (A, B, C, D) basada \
en el contexto ICFES.
- Termina SIEMPRE preguntando: "¿Cuál es tu respuesta?"

Si el usuario está respondiendo con A, B, C o D:
- Evalúa si es correcta según el contexto.
- Explica la justificación completa usando la información del PDF.
- Indica claramente si es CORRECTO ✅ o INCORRECTO ❌.
- Termina con: "SCORE:CORRECTO" si acertó o "SCORE:INCORRECTO" si falló \
(esta etiqueta la procesa el sistema automáticamente)."""


# =============================================================================
# UTILIDADES INTERNAS
# =============================================================================

def _format_history(messages: List[BaseMessage], last_n: int = 6) -> str:
    """Serializa los últimos N mensajes para inyectar en prompts del Evaluador."""
    lines = []
    for msg in messages[-last_n:]:
        role = "Usuario" if isinstance(msg, HumanMessage) else "Asistente"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)


def _extract_clean_text(content) -> str:
    """Extrae y une todo el texto limpio de la respuesta del LLM."""
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                text_parts.append(str(item["text"]))
            elif isinstance(item, str):
                text_parts.append(item)
        return "".join(text_parts) if text_parts else ""
    elif isinstance(content, dict):
        return str(content.get("text", content))
    return str(content)


# =============================================================================
# NODOS DEL GRAFO
# =============================================================================

def node_router(state: AgentState, llm) -> AgentState:
    """
    Nodo Enrutador: clasifica la intención del último mensaje del usuario.
    SRS §2.2 · FR §2.2 punto 1.
    """
    last_human = next(
        (m for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
        None,
    )
    if last_human is None:
        return {**state, "intent": "PROFESOR"}

    prompt   = ROUTER_PROMPT.format(message=last_human.content)
    response = llm.invoke([HumanMessage(content=prompt)])
    content = _extract_clean_text(response.content)
    raw = str(content).strip().upper()

    intent   = "EVALUADOR" if "EVALUADOR" in raw else "PROFESOR"
    return {**state, "intent": intent}


def node_profesor(state: AgentState, llm, embeddings) -> AgentState:
    """
    Agente Profesor: responde con estructura pedagógica de 4 partes. SRS §2.2.2.
    """
    last_human = next(
        (m for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
        None,
    )
    question = last_human.content if last_human else ""
    context  = retrieve_context(question, embeddings)

    prompt   = PROFESOR_PROMPT.format(context=context, question=question)
    response = llm.invoke([HumanMessage(content=prompt)])
    clean_content = _extract_clean_text(response.content)
    ai_msg   = AIMessage(content=clean_content)

    return {**state, "messages": state["messages"] + [ai_msg]}


def node_evaluador(state: AgentState, llm, embeddings) -> AgentState:
    """
    Agente Evaluador: formula preguntas tipo ICFES y califica respuestas.
    SRS §2.2.3.
    """
    last_human = next(
        (m for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
        None,
    )
    message = last_human.content if last_human else ""
    context = retrieve_context(message, embeddings)
    history = _format_history(state["messages"])

    prompt   = EVALUADOR_PROMPT.format(context=context, history=history, message=message)
    response = llm.invoke([HumanMessage(content=prompt)])
    content  = _extract_clean_text(response.content)

    score_correct   = state["score_correct"]
    score_incorrect = state["score_incorrect"]

    content_upper = content.upper()

    # Evaluamos usando expresiones regulares para tolerar espacios extra
    if "SCORE:CORRECTO" in content_upper or "SCORE: CORRECTO" in content_upper:
        score_correct += 1
        content = re.sub(r"(?i)SCORE:\s*CORRECTO", "", content)
    elif "SCORE:INCORRECTO" in content_upper or "SCORE: INCORRECTO" in content_upper:
        score_incorrect += 1
        content = re.sub(r"(?i)SCORE:\s*INCORRECTO", "", content)

    ai_msg = AIMessage(content=content.strip())
    return {
        **state,
        "messages":        state["messages"] + [ai_msg],
        "score_correct":   score_correct,
        "score_incorrect": score_incorrect,
    }


# =============================================================================
# CONSTRUCCIÓN Y COMPILACIÓN DEL GRAFO
# =============================================================================

def build_graph(llm, embeddings):
    """
    Construye y compila el grafo LangGraph con el Enrutador y los dos agentes.
    SRS §2.2. Retorna el grafo compilado listo para invocar.
    """
    from langgraph.graph import StateGraph, END

    def router_node(state: AgentState) -> AgentState:
        return node_router(state, llm)

    def profesor_node(state: AgentState) -> AgentState:
        return node_profesor(state, llm, embeddings)

    def evaluador_node(state: AgentState) -> AgentState:
        return node_evaluador(state, llm, embeddings)

    def route_decision(state: AgentState) -> str:
        return state.get("intent", "PROFESOR")

    g = StateGraph(AgentState)
    g.add_node("router",    router_node)
    g.add_node("profesor",  profesor_node)
    g.add_node("evaluador", evaluador_node)

    g.set_entry_point("router")
    g.add_conditional_edges(
        "router",
        route_decision,
        {"PROFESOR": "profesor", "EVALUADOR": "evaluador"},
    )
    g.add_edge("profesor",  END)
    g.add_edge("evaluador", END)

    return g.compile()

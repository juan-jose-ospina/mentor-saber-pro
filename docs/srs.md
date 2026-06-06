# System Requirements Specification (SRS)

**Proyecto:** Mentor Saber Pro - Asistente Inteligente con RAG y Multiagentes
**Versión:** 2.0 (Final)
**Fecha:** Junio 2026

---

## 1. Introducción

### 1.1 Propósito

El propósito de este documento es definir exhaustivamente los requisitos funcionales (FR) y no funcionales (NFR) para la construcción de "Mentor Saber Pro". Este sistema es un asistente educativo multiagente impulsado por un pipeline RAG (Retrieval-Augmented Generation), diseñado para preparar a estudiantes para las Pruebas de Estado (ICFES / Saber Pro) en Colombia.

### 1.2 Alcance del Sistema

El sistema actuará como una aplicación web local (SPA) que procesa preguntas en lenguaje natural. No utilizará bases de datos en la nube. Todo el conocimiento del sistema provendrá estrictamente de un corpus local de cuadernillos oficiales del ICFES en formato PDF. El sistema orquestará dos agentes de IA con personalidades distintas (Profesor y Evaluador) y será capaz de emitir reportes de desempeño en formato PDF.

---

## 2. Descripción General y Arquitectura

### 2.1 Stack Tecnológico Obligatorio

El agente programador deberá utilizar estrictamente las siguientes tecnologías:

- **Lenguaje:** Python 3.11+
- **Interfaz de Usuario:** Streamlit (`streamlit`)
- **Orquestador Multiagente:** LangGraph (`langgraph`, `langchain-core`)
- **LLM Principal:** Gemini 1.5 Flash vía Google AI Studio (`langchain-google-genai`)
- **Base de Datos Vectorial:** ChromaDB en modo embedded (`langchain-chroma`)
- **Embeddings:** `nomic-embed-text-v1.5` vía `sentence-transformers` (`langchain-huggingface`)
- **Re-ranking (Cross-Encoder):** `ms-marco-MiniLM-L-6-v2` (opcionalmente integrado con `sentence-transformers`)
- **Procesamiento PDF:** PyMuPDF (`fitz`)
- **Generación de Reportes PDF (Skill):** ReportLab (`reportlab`)

### 2.2 Roles de los Agentes

El sistema implementará un grafo de estado con LangGraph que coordine los siguientes nodos funcionales:

1. **Nodo Router (Enrutador):** Clasifica la intención del mensaje del usuario mediante un prompt estructurado. Retorna `PROFESOR` si el usuario pide teoría o explicaciones. Retorna `EVALUADOR` si el usuario pide simulacros o está respondiendo a una pregunta (A, B, C, D).
2. **Agente Profesor:** Su rol es pedagógico. Consume el RAG y estructura sus respuestas obligatoriamente en cuatro partes: 1. Definición, 2. Ejemplo práctico, 3. Tip para el examen, 4. Fuente consultada (nombre del PDF).
3. **Agente Evaluador:** Su rol es calificar. Formula preguntas de opción múltiple basadas en el RAG, espera la respuesta del usuario, evalúa si es correcta/incorrecta (usando la justificación del PDF), retroalimenta al usuario y actualiza el contador de puntaje en el Estado Global.

---

## 3. Requisitos Funcionales (FR)

### FR1: Gestión del Estado (LangGraph State)

- **FR1.1:** El sistema debe definir una clase `AgentState` (usando `TypedDict` o Pydantic) que almacene la memoria de la sesión.
- **FR1.2:** El estado debe contener: `messages` (lista de mensajes de LangChain), `intent` (cadena de texto para enrutamiento), `score_correct` (entero) y `score_incorrect` (entero).

### FR2: Pipeline RAG (Ingesta y Recuperación)

- **FR2.1 (Ingesta):** El sistema debe leer todos los archivos `.pdf` ubicados en el directorio `/data`.
- **FR2.2 (Chunking):** Los textos extraídos deben dividirse utilizando `RecursiveCharacterTextSplitter` con un `chunk_size` de 512 y un `chunk_overlap` de 64.
- **FR2.3 (Indexación):** Los vectores se almacenarán en un directorio local `./chroma_db`. Los metadatos de cada chunk deben incluir el nombre del archivo fuente (ej. `cuadernillo_matematicas_2026.pdf`).
- **FR2.4 (Recuperación Mejorada):** Al realizar una consulta, el sistema debe usar búsqueda por similitud para extraer los fragmentos más relevantes y pasarlos como contexto en el System Prompt de los agentes.

### FR3: Interfaz de Usuario (Streamlit)

- **FR3.1:** La interfaz debe mostrar el historial de chat de forma interactiva (`st.chat_message`).
- **FR3.2:** Debe incluir una barra lateral (`st.sidebar`) que contenga:
  - Un campo de texto seguro (`type="password"`) para que el usuario ingrese su API Key de Google (Gemini).
  - Un panel con los puntajes actuales (Respuestas Correctas e Incorrectas).
  - Un botón para disparar la ingesta manual de PDFs (Simulación de MCP).
  - Un botón para ejecutar la Skill de generación de reportes.

### FR4: Skills y MCP (Model Context Protocol)

- **FR4.1 (FileSystem MCP Simulado):** La función de indexación de PDFs debe poder ejecutarse en tiempo de ejecución desde la interfaz sin necesidad de reiniciar el servidor, actualizando la base vectorial ChromaDB.
- **FR4.2 (Skill de Reporte):** Debe existir una función en Python que lea las variables `score_correct` y `score_incorrect` del estado de Streamlit, y utilice la librería `reportlab` para crear un archivo PDF local llamado `reporte_desempeno_icfes.pdf`. Este archivo debe quedar disponible para descarga vía `st.download_button`.

---

## 4. Requisitos No Funcionales (NFR)

- **NFR1 (Restricción de Frameworks):** Bajo ninguna circunstancia se debe utilizar React, Node.js, FastAPI, Flask, Docker o Pinecone. Todo el código debe residir en archivos Python ejecutables localmente.
- **NFR2 (Manejo de Errores):** El sistema debe prevenir caídas en la interfaz si el usuario no ha ingresado la API Key, mostrando un mensaje de advertencia (`st.warning`).
- **NFR3 (Modularidad):** El código resultante debe ser lo suficientemente limpio para ser explicado línea por línea. Se acepta un enfoque de archivo monolítico (`app.py`) para facilitar el despliegue de la demostración, siempre y cuando las responsabilidades (Estado, RAG, Agentes, UI) estén claramente seccionadas y comentadas.
- **NFR4 (Protección de Entorno):** El código debe inyectar la API Key ingresada por el usuario en `os.environ["GOOGLE_API_KEY"]` para que `langchain-google-genai` la detecte automáticamente.

# Mentor Saber Pro

## Descripción Académica
Mentor Saber Pro es un sistema avanzado basado en la arquitectura RAG (Retrieval-Augmented Generation) y orquestación multiagente diseñado para apoyar la preparación de estudiantes para las pruebas ICFES Saber Pro. El sistema proporciona un entorno interactivo mediante el cual los usuarios pueden consultar material de estudio, recibir explicaciones detalladas y ser evaluados de manera dinámica. Esta solución se fundamenta en la integración de modelos de lenguaje de gran escala (LLMs) con bases de conocimiento locales y específicas del dominio, garantizando respuestas precisas, contextualizadas y pedagógicamente estructuradas.

## Arquitectura del Sistema
El diseño arquitectónico del proyecto se divide en diferentes componentes interactivos y flujos de procesamiento. Para un análisis detallado, consulte los siguientes diagramas técnicos:
- [Diagrama de Arquitectura](docs/diagrama_arquitectura.md): Representación general del flujo entre el Frontend (Streamlit), el Orquestador (LangGraph), la Base de Datos Vectorial (ChromaDB) y el Modelo de Lenguaje (Gemini 1.5 Flash).
- [Diagrama RAG](docs/diagrama_rag.md): Flujo detallado del proceso de ingesta de documentos PDF mediante PyMuPDF, fragmentación de texto, generación de embeddings vectoriales (nomic-embed-text-v1.5) y recuperación de información.
- [Diagrama de Agentes](docs/diagrama_agentes.md): Diagrama de estados que ilustra la lógica de enrutamiento del sistema, donde un nodo especializado decide delegar las tareas al Agente Profesor o al Agente Evaluador según la intención del usuario.

## Stack Tecnológico
- Lenguaje de Programación: Python 3.11+
- Interfaz de Usuario (Frontend): Streamlit
- Orquestación Multiagente: LangGraph
- Cadenas y Utilidades LLM: LangChain
- Base de Datos Vectorial: ChromaDB
- Generación de Embeddings: Nomic-embed-text-v1.5
- Modelo de Lenguaje (LLM): Gemini 1.5 Flash
- Procesamiento de Documentos: PyMuPDF
- Generación de Reportes: ReportLab

## Instrucciones de Instalación y Ejecución

1. Creación y activación del entorno virtual:
   Para sistemas operativos basados en Windows (PowerShell):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   Para sistemas UNIX/macOS:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Instalación de dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configuración de Variables de Entorno:
   Cree un archivo `.env` en la raíz del proyecto y configure su clave API para el modelo de Google:
   ```env
   GOOGLE_API_KEY=su_clave_api_aqui
   ```

4. Ejecución del aplicativo:
   ```bash
   streamlit run src/app.py
   ```

## Estructura del Repositorio
```text
mentor-saber-pro/
├── docs/
│   ├── diagrama_agentes.md
│   ├── diagrama_arquitectura.md
│   ├── diagrama_rag.md
│   ├── prd.md
│   └── srs.md
├── src/
│   ├── agents.py
│   ├── app.py
│   ├── rag.py
│   ├── skills.py
│   └── state.py
├── tests/
├── .env.example
├── README.md
└── requirements.txt
```

## Autores
- Juan José Bedoya Ramos
- Juan José Ospina Ospina

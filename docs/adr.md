# ADR-001: Selección del Stack Tecnológico Base para RAG Multiagente

## Estado
Aceptado

## Fecha
Junio 2026

## Contexto
El proyecto "Mentor Saber Pro" surge de la necesidad imperativa de proporcionar un sistema educativo avanzado y accesible para la preparación de las pruebas estatales ICFES/Saber Pro. Dada la naturaleza del problema, se requiere un sistema capaz de procesar cuadernillos de pruebas, generar retroalimentación pedagógica y simular evaluaciones. Las restricciones primarias del proyecto incluyen un presupuesto operativo estrictamente limitado (idealmente tendiendo a cero en costos de infraestructura base) y un tiempo de desarrollo reducido que exige alta iteración. Por consiguiente, se requiere una arquitectura que maximice la eficiencia, minimice la latencia y evite la dependencia de servicios en la nube costosos, manteniendo al mismo tiempo un alto rigor académico y técnico en la ejecución del paradigma de Generación Aumentada por Recuperación (RAG) y la orquestación de múltiples agentes.

## Decisiones

### 1. LangGraph para la Orquestación Multiagente
Se ha decidido adoptar LangGraph en lugar de frameworks de abstracción de nivel superior (caja negra). La justificación técnica radica en la necesidad de un control de estado explícito y un enrutamiento predecible. LangGraph permite definir arquitecturas cíclicas y flujos de trabajo deterministas mediante grafos, lo que resulta crítico para coordinar las interacciones entre el agente "Profesor" y el agente "Evaluador" sin perder la trazabilidad de la memoria conversacional ni el estado de la evaluación.

### 2. Gemini 1.5 Flash vía Google AI Studio
El motor de razonamiento principal será Gemini 1.5 Flash, consumido a través de la API de Google AI Studio. Esta decisión se fundamenta en tres pilares: una latencia de inferencia significativamente reducida, una ventana de contexto masiva que permite procesar y correlacionar extensos fragmentos de cuadernillos simultáneamente, y la disponibilidad de una capa gratuita robusta que cumple con las restricciones financieras del proyecto.

### 3. ChromaDB Local y nomic-embed-text-v1.5
Para la base de datos vectorial se implementará ChromaDB en modo local (embebido), utilizando el modelo de embeddings `nomic-embed-text-v1.5`. Esta configuración permite la ejecución directa en el entorno del usuario sin requerir aprovisionamiento de infraestructura cloud (bases de datos administradas). El modelo Nomic fue seleccionado por su excepcional rendimiento y capacidad de generar representaciones semánticas densas, optimizando el proceso de recuperación (Retrieval) en la arquitectura RAG.

### 4. Streamlit para la Interfaz de Usuario
El frontend se construirá utilizando Streamlit. La justificación de esta decisión es el desarrollo ágil que proporciona para interfaces de usuario reactivas y unificadas directamente en Python. Esto elimina la necesidad de mantener un stack separado de frontend/backend, reduciendo drásticamente la complejidad arquitectónica y el tiempo de entrega (Time-to-Market), permitiendo iteraciones rápidas sobre el sistema RAG subyacente.

### 5. ReportLab para la Generación de "Skills" (Reportes)
La funcionalidad de generación de reportes PDF detallados (Skills) se implementará mediante la biblioteca ReportLab. A diferencia de las alternativas basadas en plantillas HTML a PDF, ReportLab ofrece un control programático absoluto sobre el lienzo del documento. Esto asegura precisión milimétrica en la disposición de métricas, gráficos y evaluaciones formales, cumpliendo con los estándares de un reporte académico profesional.

### 6. MCP Simulado y Sistema de Archivos Dinámico
La ingesta de nuevos cuadernillos y material de estudio se manejará mediante un patrón de Protocolo de Contexto de Modelo (MCP) simulado, basado en un sistema de archivos dinámico. La justificación técnica es permitir la escalabilidad y la actualización del corpus de conocimiento en tiempo real. Esta arquitectura asegura que el sistema pueda ingerir, fragmentar e indexar nuevos documentos sin necesidad de reiniciar los servicios, garantizando la continuidad operativa y una expansión fluida del dominio de conocimiento.

## Consecuencias

**Impactos Positivos:**
- **Costo Operativo Cero ($0):** La combinación de ChromaDB local, Gemini 1.5 Flash (capa gratuita) y Streamlit elimina por completo los gastos recurrentes de infraestructura en la fase de prototipado y operación base.
- **Mantenibilidad:** El uso exclusivo de Python en todo el stack (desde la ingesta hasta la interfaz de usuario) reduce la fricción cognitiva y facilita el mantenimiento a largo plazo.
- **Trazabilidad:** LangGraph asegura que las interacciones complejas puedan auditarse paso a paso.

**Trade-offs (Compromisos):**
- **Tiempo de Indexación Inicial:** Al utilizar recursos locales (CPU) para la vectorización de los cuadernillos con ChromaDB y Nomic, los tiempos iniciales de indexación pueden ser elevados, lo que requiere estrategias de carga asíncrona o pre-indexación en la experiencia de usuario final.
- **Escalabilidad Horizontal:** Al depender de estados en memoria (Streamlit session state y Chroma local), la escalabilidad masiva a múltiples usuarios concurrentes en servidores distribuidos requerirá una refactorización hacia bases de datos externas en fases futuras.

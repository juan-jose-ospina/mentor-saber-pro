# Product Requirements Document (PRD)

**Producto:** Mentor Saber Pro
**Versión:** 1.0
**Fecha:** Junio 2026

---

## 1. Visión y Propósito del Producto

**Mentor Saber Pro** es un asistente virtual educativo basado en Inteligencia Artificial (Multiagentes + RAG) diseñado para democratizar la preparación para las pruebas de Estado (Saber 11 / Saber Pro) en Colombia.

El problema actual es que miles de estudiantes se preparan con cuadernillos en PDF estáticos, sin recibir retroalimentación inmediata sobre sus errores ni explicaciones claras de los conceptos evaluados. Mentor Saber Pro resuelve este dolor (pain point) transformando esos documentos estáticos en una experiencia interactiva, donde el estudiante puede conversar con el material de estudio, pedir explicaciones teóricas y realizar simulacros calificados en tiempo real.

---

## 2. Público Objetivo (User Personas)

**Perfil Principal: El Estudiante Colombiano (Grado 11 o Universitario)**

- **Necesidad:** Prepararse para las pruebas ICFES para acceder a educación superior o graduarse.
- **Frustración:** No entiende por qué una respuesta es correcta o incorrecta al leer los cuadernillos oficiales. Necesita un tutor paciente que le explique los conceptos desde cero y lo ponga a prueba.
- **Contexto Tecnológico:** Busca soluciones rápidas, accesibles desde un navegador, y prefiere interfaces limpias tipo chat (estilo WhatsApp o ChatGPT).

---

## 3. Propuesta de Valor

- **Interactividad basada en evidencia:** El sistema no "inventa" respuestas; utiliza un pipeline RAG anclado exclusivamente a los cuadernillos oficiales del ICFES.
- **Tutoría Dual (Multiagente):** Ofrece dos experiencias en una. Un "Profesor" para enseñar teoría y un "Evaluador" para poner a prueba el conocimiento mediante simulacros.
- **Medición de Progreso:** Permite al usuario materializar su esfuerzo exportando un reporte de desempeño en PDF al finalizar su sesión de estudio.

---

## 4. Casos de Uso Principales (User Journeys)

**Caso de Uso 1: Aprender un Concepto Nuevo**

1. El usuario ingresa a la plataforma y pregunta: _"¿Qué es la lectura crítica argumentativa?"_.
2. El sistema clasifica la intención y activa al Agente Profesor.
3. El Agente Profesor busca en el corpus del ICFES y responde con una estructura pedagógica clara (Definición, Ejemplo, Tip para el examen y Fuente).

**Caso de Uso 2: Realizar un Simulacro de Prueba**

1. El usuario solicita: _"Quiero una pregunta de matemáticas"_.
2. El sistema activa al Agente Evaluador, quien busca una pregunta en el corpus y se la presenta al usuario con opciones (A, B, C, D).
3. El usuario responde (ej. _"Es la C"_).
4. El Agente Evaluador califica la respuesta (CORRECTO/INCORRECTO), explica el porqué basándose en la justificación oficial del cuadernillo, y actualiza el puntaje global de la sesión.

**Caso de Uso 3: Exportar Resultados (Skill)**

1. Tras realizar varias preguntas, el usuario hace clic en el botón "Generar Reporte PDF".
2. El sistema consolida las respuestas correctas e incorrectas de la sesión actual.
3. Se genera y descarga un archivo PDF formal con el resumen del desempeño y recomendaciones de estudio.

---

## 5. Criterios de Éxito y Métricas (KPIs)

Para considerar que el Producto Mínimo Viable (MVP) es exitoso durante la demostración, debe cumplir con:

- **Precisión del Enrutamiento:** El orquestador LangGraph debe ser capaz de discernir entre una consulta teórica y una solicitud de simulacro con un 100% de precisión en los tests manuales.
- **Cero Alucinaciones:** Las respuestas deben citar explícitamente los cuadernillos del ICFES almacenados en la carpeta `/data`.
- **Funcionalidad End-to-End:** El usuario debe poder completar el ciclo completo: Ingestar documentos -> Hacer pregunta -> Responder simulacro -> Descargar PDF de reporte, sin errores de ejecución (crashes) en la interfaz de Streamlit.

---

## 6. Restricciones del Producto

- **Costo Cero:** El producto debe operar exclusivamente con APIs gratuitas (Google AI Studio - Gemini 3.5 Flash) y librerías Open Source locales (ChromaDB, LangChain, Streamlit).
- **Ausencia de Nube Base de Datos:** Por restricciones de arquitectura de la entrega, no se utilizarán bases de datos persistentes en la nube para guardar el progreso histórico del usuario entre sesiones distintas. Todo el estado se maneja en la memoria de la sesión actual mediante LangGraph y Streamlit.

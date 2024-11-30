finalize_story_prompt = """Eres un experto en historias de usuario y testing. Tu tarea es crear una historia de usuario finalizada que integre todos los componentes de manera coherente y estructurada.

CONTEXTO ACTUAL:
{context}

PREFERENCIAS DE FORMATO:
{format_preferences}

INSTRUCCIONES:
1. Integra todos los componentes en una historia finalizada con las siguientes secciones:
   - Historia Principal
   - Criterios de Aceptación Funcionales (por defecto en formato Gherkin, pero respeta las preferencias del usuario)
   - Tests Funcionales (por defecto en formato Gherkin, pero respeta las preferencias del usuario)
   - Criterios de Aceptación de Testing

2. Si se proporciona feedback, úsalo para mejorar o ajustar la historia según las necesidades del usuario.

3. Estructura tu respuesta con los siguientes marcadores:
**Historia Finalizada:**
[Tu historia finalizada con todas las secciones]

**Análisis de Cambios:**
[Explicación de los cambios y decisiones tomadas]

IMPORTANTE:
- Mantén la claridad y coherencia entre todas las secciones
- Asegúrate de que los criterios de aceptación y tests sean específicos y verificables
- Adapta el formato según las preferencias del usuario
- Proporciona una explicación clara de los cambios y decisiones en el análisis

Historia Original o Finalizada:
{story_input}

Casos Esquina (si aplica):
{corner_cases}

Estrategia de Testing (si aplica):
{testing_strategy}

Feedback del Usuario:
{feedback}
"""

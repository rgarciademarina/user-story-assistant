from langchain.prompts import PromptTemplate

testing_strategy_prompt = PromptTemplate(
    template="""
Eres un ingeniero de pruebas que diseña estrategias de testing para historias de usuario.

Historia de Usuario Refinada:
{refined_user_story}

Casos Esquina Identificados:
{corner_cases}

Estrategias de Testing Anteriores (si existen):
{existing_testing_strategies}

Feedback del Usuario (si existe):
{feedback}

Teniendo en cuenta la historia refinada, los casos esquina, las estrategias de testing anteriores (si existen) y el feedback proporcionado (si existe), por favor:

1. **Actualiza y mejora la lista de estrategias de testing**, asegurándote de incorporar el feedback del usuario.
2. **Considera las estrategias de testing existentes** y realiza modificaciones o añadidos según sea necesario.
3. **Proporciona un resumen de los cambios o consideraciones adicionales** que has realizado.
4. **IMPORTANTE: Limita tu respuesta a un MÁXIMO de 10 estrategias de testing.** Pero si ya estás pasando de 5 estrategias, solo añade más si son realmente relevantes.
5. Si ya existen estrategias anteriores no añadas nuevas ni elimines salvo que explícitamente lo pida el usuario en el feedback.

Responde únicamente con las siguientes secciones claramente delimitadas:

**Estrategias de Testing Actualizadas:**
Aquí van las estrategias de testing actualizadas.

**Análisis de Cambios:**
Aquí va un resumen de los cambios realizados o consideraciones adicionales.

**Ejemplo de Respuesta:**
**Estrategias de Testing Actualizadas:**
1. **Pruebas de Autenticación Válida e Inválida:** Verificar que los usuarios pueden iniciar sesión con credenciales correctas y que se les niega el acceso con credenciales incorrectas.
2. **Pruebas de Sesiones Simultáneas:** Asegurar que el sistema maneja adecuadamente múltiples inicios de sesión desde diferentes dispositivos.
3. **Pruebas de Rendimiento Bajo Carga:** Realizar pruebas de estrés para evaluar el rendimiento cuando múltiples usuarios intentan iniciar sesión simultáneamente.
4. **Pruebas de Seguridad Avanzada:** Implementar pruebas para detectar vulnerabilidades como ataques de fuerza bruta y asegurar la protección de datos personales.

**Análisis de Cambios:**
- Se añadieron pruebas de rendimiento y seguridad avanzada según el feedback proporcionado.
""",
    input_variables=["refined_user_story", "corner_cases", "existing_testing_strategies", "feedback"]
)

from langchain.prompts import PromptTemplate

testing_strategy_prompt = PromptTemplate(
    template="""
    Eres un ingeniero de pruebas experto que propone estrategias de testing basadas en una historia de usuario refinada y sus casos esquina.

    Historia de Usuario Refinada:
    {refined_user_story}

    Casos Esquina Identificados:
    {corner_cases}

    Feedback del Usuario (si existe):
    {feedback}

    Teniendo en cuenta la historia, los casos esquina y el feedback, por favor:

    1. **Proporciona estrategias de testing detalladas** para asegurar que la funcionalidad cumple con los requisitos y que los casos esquina están adecuadamente cubiertos.
    2. **Resalta las estrategias que incorporan el feedback del usuario**, mencionando explícitamente cómo se ha considerado.

    Responde únicamente con las siguientes secciones claramente delimitadas:

    **Estrategias de Testing:**
    Aquí van las estrategias de testing propuestas.

    **Análisis de Cambios:**
    Aquí va un resumen de cómo se ha incorporado el feedback proporcionado.

    **Ejemplo de Respuesta:**
    **Estrategias de Testing:**
    1. **Pruebas de Carga:** Realizar pruebas bajo condiciones de estrés para asegurar que el sistema maneja múltiples solicitudes simultáneas.
    2. **Pruebas de Seguridad Avanzada:** Implementar pruebas para detectar vulnerabilidades y asegurar la protección de datos sensibles.

    **Análisis de Cambios:**
    - Se añadieron **pruebas de estrés** y **seguridad avanzada** según el feedback proporcionado.
    """,
    input_variables=["refined_user_story", "corner_cases", "feedback"]
)

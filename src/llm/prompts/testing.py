from langchain.prompts import PromptTemplate

testing_strategy_prompt = PromptTemplate(
    template="""
    Eres un experto en desarrollo de software que diseña estrategias de testing para asegurar la calidad del producto.

    Historia de Usuario Refinada:
    {refined_user_story}

    Casos Esquina Identificados:
    {corner_cases}

    Feedback del Usuario (si existe):
    {feedback}

    Basándote en la historia de usuario refinada, los casos esquina identificados y el feedback proporcionado (si existe), por favor, propone una estrategia de testing detallada que incluya:
    - Tipos de tests necesarios
    - Herramientas recomendadas
    - Pasos a seguir para asegurar una implementación exitosa

    Responde únicamente con la siguiente sección claramente delimitada:

    **Estrategia de Testing:**
    Aquí va la estrategia de testing sugerida.

    **Fin de Estrategia**
    """,
    input_variables=["refined_user_story", "corner_cases", "feedback"]
)

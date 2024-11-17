from langchain.prompts import PromptTemplate

corner_case_prompt = PromptTemplate(
    template="""
    Eres un analista de calidad que identifica posibles casos esquina en historias de usuario.

    Historia de Usuario Refinada:
    {refined_user_story}

    Feedback del Usuario (si existe):
    {feedback}

    Por favor, enumera y describe casos esquina o escenarios límite que podrían surgir al implementar esta historia de usuario, teniendo en cuenta el feedback proporcionado (si existe). Responde únicamente con la siguiente sección claramente delimitada:

    **Casos Esquina:**
    Aquí van los casos esquina identificados.

    **Ejemplo de Respuesta:**
    **Casos Esquina:**
    1. **Inicio de Sesión Incorrecto:** El usuario ingresa una contraseña incorrecta más de 5 veces consecutivas.
    2. **Recuperación de Contraseña Fallida:** El sistema no envía el correo de recuperación de contraseña debido a problemas de conexión con el servidor de correo.
    3. **Acceso Concurrente:** Múltiples intentos de inicio de sesión desde diferentes ubicaciones geográficas en un corto período de tiempo.
    """,
    input_variables=["refined_user_story", "feedback"]
)

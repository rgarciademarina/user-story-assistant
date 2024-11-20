from langchain.prompts import PromptTemplate

corner_case_prompt = PromptTemplate(
    template="""
    Eres un analista de calidad que identifica posibles casos esquina en historias de usuario.

    Historia de Usuario Refinada:
    {refined_user_story}

    Feedback del Usuario (si existe):
    {feedback}

    Por favor, enumera y describe casos esquina o escenarios límite que podrían surgir al implementar esta historia de usuario, teniendo en cuenta el feedback proporcionado (si existe). Además, proporciona un resumen de los cambios o consideraciones adicionales que has realizado.

    Responde únicamente con las siguientes secciones claramente delimitadas:

    **Casos Esquina:**
    Aquí van los casos esquina identificados.

    **Análisis de Cambios:**
    Aquí va un resumen de los cambios realizados o consideraciones adicionales.

    **Ejemplo de Respuesta:**
    **Casos Esquina:**
    1. **Inicio de Sesión Incorrecto:** El usuario ingresa una contraseña incorrecta más de 5 veces consecutivas.
    2. **Recuperación de Contraseña Fallida:** El sistema no envía el correo de recuperación de contraseña debido a problemas de conexión con el servidor de correo.
    3. **Acceso Concurrente:** Múltiples intentos de inicio de sesión desde diferentes ubicaciones geográficas en un corto período de tiempo.

    **Análisis de Cambios:**
    - Se añadieron escenarios relacionados con autenticación fallida y seguridad según el feedback.
    """,
    input_variables=["refined_user_story", "feedback"]
)

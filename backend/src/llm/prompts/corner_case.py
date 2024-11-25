from langchain.prompts import PromptTemplate

corner_case_prompt = PromptTemplate(
    template="""
    Eres un analista de calidad que identifica posibles casos esquina en historias de usuario.

    Historia de Usuario Refinada:
    {refined_user_story}

    Casos Esquina Anteriores (si existen):
    {existing_corner_cases}

    Feedback del Usuario (si existe):
    {feedback}

    Teniendo en cuenta la historia de usuario refinada, los casos esquina anteriores (si existen) y el feedback proporcionado (si existe), por favor:

    1. **Actualiza y mejora la lista de casos esquina**, asegurándote de incorporar el feedback del usuario.
    2. **Considera los casos esquina existentes** y realiza modificaciones o añadidos según sea necesario.
    3. **Proporciona un resumen de los cambios o consideraciones adicionales** que has realizado.

    Responde únicamente con las siguientes secciones claramente delimitadas:

    **Casos Esquina Actualizados:**
    Aquí van los casos esquina actualizados.

    **Análisis de Cambios:**
    Aquí va un resumen de los cambios realizados o consideraciones adicionales.

    **Ejemplo de Respuesta:**
    **Casos Esquina Actualizados:**
    1. **Intentos de Inicio de Sesión Fallidos:** El usuario ingresa una contraseña incorrecta repetidamente.
    2. **Acceso desde Ubicaciones No Reconocidas:** Intentos de inicio de sesión desde ubicaciones geográficas inusuales.
    3. **Autenticación de Dos Factores Fallida:** El usuario no puede completar la autenticación de dos factores debido a problemas con el dispositivo secundario.
    4. **Bloqueo por Inactividad:** La sesión del usuario caduca después de un período de inactividad sin guardar cambios.

    **Análisis de Cambios:**
    - Se añadieron casos relacionados con autenticación de dos factores y bloqueo por inactividad según el feedback proporcionado.
    - Se actualizó el caso de acceso desde ubicaciones no reconocidas para enfatizar la seguridad.
    """,
    input_variables=["refined_user_story", "existing_corner_cases", "feedback"]
)

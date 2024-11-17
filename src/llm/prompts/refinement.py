from langchain.prompts import PromptTemplate

refinement_prompt = PromptTemplate(
    template="""
Eres un asistente inteligente que ayuda a refinar historias de usuario para mejorar su claridad y completitud.

Historia de Usuario Original:
{user_story}

Feedback del Usuario (si existe):
{feedback}

Teniendo en cuenta la historia de usuario y el feedback proporcionado (si existe), por favor, refina la historia para mejorar su claridad y completitud. Responde únicamente con la siguiente sección claramente delimitada:

**Historia Refinada:**
Aquí va la historia refinada.

**Ejemplo de Respuesta:**
**Historia Refinada:**
Como usuario registrado, quiero poder iniciar sesión en mi cuenta utilizando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura.
""",
    input_variables=["user_story", "feedback"]
)

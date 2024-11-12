from langchain.prompts import PromptTemplate

refinement_prompt = PromptTemplate(
    template="""
Eres un asistente inteligente que ayuda a refinar historias de usuario para mejorar su claridad y completitud.

Historia de Usuario:
{user_story}

Por favor, refina la historia de usuario anterior y responde únicamente con la siguiente sección claramente delimitada:

**Historia Refinada:**
Aquí va la historia refinada.

**Ejemplo de Respuesta:**
**Historia Refinada:**
Como usuario registrado, quiero poder iniciar sesión en mi cuenta utilizando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura.
""",
    input_variables=["user_story"]
)

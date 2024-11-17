from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from src.llm.service import LLMService
from src.llm.config import get_llm_config
from uuid import UUID

router = APIRouter()
llm_service = LLMService(get_llm_config())

class ProposeTestingStrategyRequest(BaseModel):
    session_id: UUID | None = Field(
        None,
        json_schema_extra={
            "description": "ID de sesión para mantener el contexto de la conversación. Si no se proporciona, se creará una nueva sesión."
        }
    )
    story: str = Field(
        ...,
        json_schema_extra={
            "example": "Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura.",
            "description": "Historia de usuario refinada para la propuesta de estrategias de testing."
        }
    )
    corner_cases: List[str] = Field(
        ...,
        json_schema_extra={
            "example": [
                "Intentos de inicio de sesión con contraseñas incorrectas",
                "Acceso simultáneo desde múltiples dispositivos"
            ],
            "description": "Lista de casos esquina identificados para la historia de usuario."
        }
    )
    feedback: str | None = Field(
        None,
        json_schema_extra={
            "example": "Incluir pruebas de rendimiento y seguridad en la estrategia de testing.",
            "description": "Feedback opcional del usuario sobre las estrategias de testing propuestas anteriormente."
        }
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "story": "Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura.",
                "corner_cases": [
                    "Intentos de inicio de sesión con contraseñas incorrectas",
                    "Acceso simultáneo desde múltiples dispositivos"
                ],
                "feedback": "Incluir pruebas de rendimiento y seguridad en la estrategia de testing."
            }
        }
    )

class ProposeTestingStrategyResponse(BaseModel):
    session_id: UUID = Field(
        ...,
        json_schema_extra={
            "description": "ID de sesión para usar en futuras peticiones."
        }
    )
    testing_strategies: List[str] = Field(
        ...,
        json_schema_extra={
            "example": [
                "Pruebas de autenticación con credenciales válidas e inválidas.",
                "Pruebas de concurrencia para verificar el manejo de múltiples sesiones."
            ],
            "description": "Lista de estrategias de testing propuestas basadas en la historia refinada y los casos esquina."
        }
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "testing_strategies": [
                    "Pruebas de autenticación con credenciales válidas e inválidas.",
                    "Pruebas de concurrencia para verificar el manejo de múltiples sesiones."
                ]
            }
        }
    )

@router.post(
    "/propose_testing_strategy",
    response_model=ProposeTestingStrategyResponse,
    summary="Proponer estrategias de testing para una historia de usuario",
    tags=["Refinement"]
)
async def propose_testing_strategy(request: ProposeTestingStrategyRequest):
    """
    Proponer estrategias de testing basadas en una historia de usuario refinada y sus casos esquina.

    - **session_id**: ID de sesión opcional. Si no se proporciona, se creará una nueva sesión.
    - **story**: Historia de usuario refinada en formato de texto.
    - **corner_cases**: Lista de casos esquina identificados.
    - **feedback**: Feedback opcional del usuario sobre las estrategias de testing propuestas anteriormente.
    """
    try:
        # Si no hay session_id, crear una nueva sesión
        session_id = request.session_id or llm_service.create_session()
        
        # Proponer estrategias usando el servicio LLM
        testing_strategies = await llm_service.propose_testing_strategy(
            session_id=session_id,
            refined_story=request.story,
            corner_cases=request.corner_cases,
            feedback=request.feedback
        )
        
        return {
            "session_id": session_id,
            "testing_strategies": testing_strategies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
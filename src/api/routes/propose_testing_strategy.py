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
    testing_feedback: str = Field(
        ...,
        json_schema_extra={
            "description": "Resumen de los cambios realizados por el LLM."
        }
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "testing_strategies": [
                    "1. **Pruebas de Carga:** Realizar pruebas bajo carga para asegurar que el sistema maneja múltiples solicitudes de inicio de sesión simultáneas.",
                    "2. **Pruebas de Seguridad:** Implementar pruebas para detectar y prevenir ataques de fuerza bruta.",
                    "3. **Pruebas de Autenticación de Dos Factores:** Verificar que el 2FA funciona correctamente en diversos escenarios."
                ],
                "testing_feedback": "Se añadieron pruebas de rendimiento bajo carga y pruebas de seguridad según el feedback proporcionado."
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
        result = await llm_service.propose_testing_strategy(
            session_id=session_id,
            refined_story=request.story,
            corner_cases=request.corner_cases,
            feedback=request.feedback
        )
        
        return {
            "session_id": session_id,
            "testing_strategies": result['testing_strategies'],
            "testing_feedback": result['testing_feedback']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
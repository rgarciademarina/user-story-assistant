from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from src.dependencies import get_llm_service
from src.llm.service import LLMService
from uuid import UUID

router = APIRouter()

class ProposeTestingStrategyRequest(BaseModel):
    session_id: Optional[UUID] = Field(
        None,
        json_schema_extra={
            "description": "ID de sesión para mantener el contexto de la conversación. Si no se proporciona, se creará una nueva sesión."
        }
    )
    story: str = Field(
        ...,
        json_schema_extra={
            "example": "Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura.",
            "description": "Historia de usuario refinada para la que se propondrán estrategias de testing."
        }
    )
    corner_cases: List[str] = Field(
        ...,
        json_schema_extra={
            "example": [
                "1. Intentos de inicio de sesión con credenciales incorrectas.",
                "2. Bloqueo de cuenta por múltiples intentos fallidos."
            ],
            "description": "Lista de casos esquina identificados para la historia de usuario."
        }
    )
    feedback: Optional[str] = Field(
        None,
        json_schema_extra={
            "example": "Por favor, incluir pruebas de rendimiento y seguridad.",
            "description": "Feedback opcional del usuario sobre las estrategias de testing propuestas anteriormente."
        }
    )
    existing_testing_strategies: List[str] = Field(
        default=[],
        json_schema_extra={
            "example": [
                "1. Pruebas de autenticación con credenciales válidas e inválidas.",
                "2. Pruebas de bloqueo de cuenta después de múltiples intentos fallidos."
            ],
            "description": "Lista de estrategias de testing existentes de iteraciones previas."
        }
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "story": "Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura.",
                "corner_cases": [
                    "Intentos de inicio de sesión con credenciales incorrectas",
                    "Acceso simultáneo desde múltiples dispositivos"
                ],
                "feedback": "Incluir pruebas de rendimiento y seguridad en la estrategia de testing.",
                "existing_testing_strategies": [
                    "1. Prueba de autenticación básica",
                    "2. Prueba de recuperación de contraseña"
                ]
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
    summary="Propone estrategias de testing para una historia de usuario",
    tags=["Testing"]
)
async def propose_testing_strategy(
    request: ProposeTestingStrategyRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Proponer estrategias de testing para una historia de usuario y sus casos esquina.

    - **session_id**: ID de sesión opcional. Si no se proporciona, se creará una nueva sesión.
    - **story**: Historia de usuario refinada.
    - **corner_cases**: Lista de casos esquina identificados.
    - **feedback**: Feedback opcional del usuario sobre las estrategias anteriores.
    - **existing_testing_strategies**: Lista opcional de estrategias de testing existentes.
    """
    try:
        session_id = request.session_id or llm_service.create_session()

        result = await llm_service.propose_testing_strategy(
            session_id=session_id,
            refined_story=request.story,
            corner_cases=request.corner_cases,
            feedback=request.feedback,
            existing_testing_strategies=request.existing_testing_strategies
        )

        return {
            "session_id": session_id,
            "testing_strategies": result['testing_strategies'],
            "testing_feedback": result['testing_feedback']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
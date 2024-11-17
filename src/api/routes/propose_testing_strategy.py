from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from src.llm.service import LLMService
from src.llm.config import get_llm_config

router = APIRouter()
llm_service = LLMService(get_llm_config())

class ProposeTestingStrategyRequest(BaseModel):
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

    - **story**: Historia de usuario refinada en formato de texto.
    - **corner_cases**: Lista de casos esquina identificados.
    - **feedback**: Feedback opcional del usuario sobre las estrategias de testing propuestas anteriormente.
    """
    try:
        testing_strategies = await llm_service.propose_testing_strategy(
            request.story, request.corner_cases, request.feedback
        )
        return {"testing_strategies": testing_strategies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
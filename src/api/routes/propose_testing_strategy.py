from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from uuid import UUID, uuid4
from src.llm.manager import llm_service

router = APIRouter()

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
    session_id: Optional[UUID] = Field(
        None,
        json_schema_extra={
            "example": "123e4567-e89b-12d3-a456-426614174000",
            "description": "Identificador único de la sesión para mantener el contexto."
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
                "session_id": "123e4567-e89b-12d3-a456-426614174000"
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
    - **session_id**: (Opcional) Identificador de la sesión para mantener el contexto.
    """
    try:
        session_id = str(request.session_id) if request.session_id else str(uuid4())
        
        # Utiliza LLMService para proponer estrategias de testing con el contexto de la sesión
        testing_strategies = await llm_service.propose_testing_strategy_with_context(
            request.story, request.corner_cases, session_id
        )
        
        return {"testing_strategies": testing_strategies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
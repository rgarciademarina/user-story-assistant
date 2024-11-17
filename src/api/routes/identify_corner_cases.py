from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from src.llm.service import LLMService
from src.llm.config import get_llm_config
from uuid import UUID

router = APIRouter()
llm_service = LLMService(get_llm_config())

class IdentifyCornerCasesRequest(BaseModel):
    session_id: UUID | None = Field(
        None,
        json_schema_extra={
            "description": "ID de sesión para mantener el contexto de la conversación. Si no se proporciona, se creará una nueva sesión."
        }
    )
    story: str = Field(
        ...,
        json_schema_extra={
            "example": "Como usuario registrado, quiero poder iniciar sesión en la plataforma mediante mi correo y contraseña.",
            "description": "Historia de usuario refinada en formato de texto."
        }
    )
    feedback: str | None = Field(
        None,
        json_schema_extra={
            "example": "Considerar también casos de autenticación de dos factores y bloqueos de cuenta.",
            "description": "Feedback opcional del usuario sobre los casos esquina identificados anteriormente."
        }
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "story": "Como usuario registrado, quiero poder iniciar sesión en la plataforma mediante mi correo y contraseña.",
                "feedback": "Considerar también casos de autenticación de dos factores y bloqueos de cuenta."
            }
        }
    )

class IdentifyCornerCasesResponse(BaseModel):
    session_id: UUID = Field(
        ...,
        json_schema_extra={
            "description": "ID de sesión para usar en futuras peticiones."
        }
    )
    corner_cases: List[str] = Field(
        ...,
        json_schema_extra={
            "example": [
                "Intentos de inicio de sesión con contraseñas incorrectas.",
                "Acceso simultáneo desde múltiples dispositivos."
            ],
            "description": "Lista de casos esquina identificados para la historia de usuario proporcionada."
        }
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "corner_cases": [
                    "Intentos de inicio de sesión con contraseñas incorrectas.",
                    "Acceso simultáneo desde múltiples dispositivos."
                ]
            }
        }
    )

@router.post(
    "/identify_corner_cases",
    response_model=IdentifyCornerCasesResponse,
    summary="Identifica casos esquina en una historia de usuario",
    tags=["Refinement"]
)
async def identify_corner_cases(request: IdentifyCornerCasesRequest):
    """
    Identificar posibles escenarios límite o riesgos en una historia de usuario refinada.

    - **session_id**: ID de sesión opcional. Si no se proporciona, se creará una nueva sesión.
    - **story**: Historia de usuario refinada en formato de texto.
    - **feedback**: Feedback opcional del usuario sobre los casos esquina identificados anteriormente.
    """
    try:
        # Si no hay session_id, crear una nueva sesión
        session_id = request.session_id or llm_service.create_session()
        
        # Identificar casos esquina usando el servicio LLM
        corner_cases = await llm_service.identify_corner_cases(
            session_id=session_id,
            refined_story=request.story,
            feedback=request.feedback
        )
        
        return {
            "session_id": session_id,
            "corner_cases": corner_cases
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
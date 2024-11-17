from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from uuid import UUID, uuid4
from src.llm.manager import llm_service

router = APIRouter()

class IdentifyCornerCasesRequest(BaseModel):
    story: str = Field(
        ...,
        json_schema_extra={
            "example": "Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura.",
            "description": "Historia de usuario refinada para identificar casos esquina."
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
                "session_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )

class IdentifyCornerCasesResponse(BaseModel):
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
    
    - **story**: Historia de usuario refinada en formato de texto.
    - **session_id**: (Opcional) Identificador de la sesión para mantener el contexto.
    """
    try:
        session_id = str(request.session_id) if request.session_id else str(uuid4())
        
        # Identifica casos esquina con el contexto de la sesión
        corner_cases = await llm_service.identify_corner_cases_with_context(request.story, session_id)
        
        return {"corner_cases": corner_cases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
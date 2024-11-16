from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from src.llm.service import LLMService
from src.llm.config import get_llm_config
from pydantic import ConfigDict

router = APIRouter()
llm_service = LLMService(get_llm_config())

class IdentifyCornerCasesRequest(BaseModel):
    story: str = Field(
        ...,
        json_schema_extra={
            "example": "Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura.",
            "description": "Historia de usuario refinada para identificar casos esquina."
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
    """
    try:
        corner_cases = await llm_service.identify_corner_cases(request.story)
        return {"corner_cases": corner_cases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
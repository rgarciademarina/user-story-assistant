from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from src.llm.instance import llm_service
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class IdentifyCornerCasesRequest(BaseModel):
    session_id: Optional[UUID] = Field(
        None,
        description="ID de sesión para mantener el contexto de la conversación. Si no se proporciona, se creará una nueva sesión."
    )
    story: str = Field(
        ...,
        json_schema_extra={
            "example": "Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura.",
            "description": "Historia de usuario refinada que se analizará para identificar casos esquina."
        }
    )
    feedback: Optional[str] = Field(
        None,
        json_schema_extra={
            "example": "Por favor, considerar casos de seguridad y validación de datos.",
            "description": "Feedback opcional del usuario sobre los casos esquina identificados anteriormente."
        }
    )
    existing_corner_cases: List[str] = Field(
        default=[],
        json_schema_extra={
            "example": [
                "1. Intentos de inicio de sesión con credenciales incorrectas.",
                "2. Bloqueo de cuenta por múltiples intentos fallidos."
            ],
            "description": "Lista de casos esquina existentes de iteraciones previas."
        }
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "story": "Como usuario registrado, quiero poder iniciar sesión en mi cuenta utilizando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura.",
                "feedback": "Considerar casos de autenticación de dos factores y bloqueos por inactividad.",
                "existing_corner_cases": [
                    "1. Intentos de inicio de sesión fallidos.",
                    "2. Acceso desde ubicaciones no reconocidas."
                ]}
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
    corner_cases_feedback: str = Field(
        ...,
        json_schema_extra={
            "description": "Resumen de los cambios realizados por el LLM."
        }
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "corner_cases": [
                    "1. **Intentos de Inicio de Sesión Fallidos:** El usuario ingresa una contraseña incorrecta repetidamente.",
                    "2. **Bloqueo de Cuenta por Inactividad:** La cuenta está bloqueada después de un período de inactividad prolongada."
                ],
                "corner_cases_feedback": "Se incluyeron casos relacionados con autenticación de dos factores y bloqueos por inactividad según el feedback proporcionado."
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
    - **existing_corner_cases**: Lista opcional de casos esquina existentes de iteraciones previas.
    """
    try:
        # Si no hay session_id, crear una nueva sesión
        session_id = request.session_id if request.session_id else llm_service.create_session()
        
        # Identificar casos esquina usando el servicio LLM
        result = await llm_service.identify_corner_cases(
            session_id=session_id,
            refined_story=request.story,
            feedback=request.feedback,
            existing_corner_cases=request.existing_corner_cases
        )
        
        return {
            "session_id": session_id,
            "corner_cases": result['corner_cases'],
            "corner_cases_feedback": result['corner_cases_feedback']
        }
    except ValueError as ve:
        logger.error(f"Error de validación: {str(ve)}")
        raise HTTPException(
            status_code=400,
            detail=f"ID de sesión inválido: {request.session_id}"
        )
    except KeyError as ke:
        logger.error(f"Error de sesión: {str(ke)}")
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró la sesión con ID: {session_id}"
        )
    except Exception as e:
        logger.error(f"Error al identificar casos esquina: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al identificar casos esquina: {str(e)}"
        )
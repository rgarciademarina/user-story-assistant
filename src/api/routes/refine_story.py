from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from src.dependencies import get_llm_service
from src.llm.service import LLMService
from uuid import UUID

router = APIRouter()

class RefineStoryRequest(BaseModel):
    session_id: Optional[UUID] = Field(
        None,
        json_schema_extra={
            "description": "ID de sesión para mantener el contexto de la conversación. Si no se proporciona, se creará una nueva sesión."
        }
    )
    story: str = Field(
        ...,
        json_schema_extra={
            "example": "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal.",
            "description": "Descripción detallada de la historia de usuario que desea refinar."
        }
    )
    feedback: Optional[str] = Field(
        None,
        json_schema_extra={
            "example": "Por favor, especificar el método de autenticación.",
            "description": "Feedback opcional del usuario sobre la historia refinada anterior."
        }
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "story": "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal.",
                "feedback": "Por favor, especificar el método de autenticación."
            }
        }
    )

class RefineStoryResponse(BaseModel):
    session_id: UUID = Field(
        ...,
        json_schema_extra={
            "example": "123e4567-e89b-12d3-a456-426614174000",
            "description": "ID de sesión para usar en futuras peticiones."
        }
    )
    refined_story: str = Field(
        ...,
        json_schema_extra={
            "example": "Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a los servicios y funciones disponibles en mi perfil personal.",
            "description": "Historia de usuario refinada con mejoras en claridad y completitud."
        }
    )
    refinement_feedback: str = Field(
        ...,
        json_schema_extra={
            "example": "Se especificó el método de autenticación y se detallaron los datos a los que se accede.",
            "description": "Resumen de los cambios realizados por el LLM en la historia de usuario."
        }
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "refined_story": "Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a los servicios y funciones disponibles en mi perfil personal.",
                "refinement_feedback": "Se especificó el método de autenticación y se añadió información sobre los datos personales accedidos."
            }
        }
    )

@router.post(
    "/refine_story",
    response_model=RefineStoryResponse,
    summary="Refina una historia de usuario",
    tags=["Refinement"]
)
async def refine_story(
    request: RefineStoryRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Refinar una historia de usuario para mejorar su claridad y completitud.

    - **session_id**: ID de sesión opcional. Si no se proporciona, se creará una nueva sesión.
    - **story**: Historia de usuario en formato de texto.
    - **feedback**: Feedback opcional del usuario sobre la historia refinada anterior.
    """
    try:
        session_id = request.session_id or llm_service.create_session()

        result = await llm_service.refine_story(
            session_id=session_id,
            user_story=request.story,
            feedback=request.feedback
        )

        return {
            "session_id": session_id,
            "refined_story": result['refined_story'],
            "refinement_feedback": result['refinement_feedback']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
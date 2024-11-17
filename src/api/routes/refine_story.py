from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4
from typing import Optional
from src.llm.manager import llm_service

router = APIRouter()

class RefineStoryRequest(BaseModel):
    story: str = Field(
        ...,
        json_schema_extra={
            "example": "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal.",
            "description": "Descripción detallada de la historia de usuario que desea refinar."
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
                "story": "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal.",
                "session_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )

class RefineStoryResponse(BaseModel):
    refined_story: str = Field(
        ...,
        json_schema_extra={
            "example": "Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a los servicios y funciones disponibles en mi perfil personal, como la gestión de información personal y el acceso a contenido específico.",
            "description": "Historia de usuario refinada con mejoras en claridad y completitud."
        }
    )
    session_id: str = Field(
        ...,
        json_schema_extra={
            "example": "123e4567-e89b-12d3-a456-426614174000",
            "description": "Identificador único de la sesión para futuras interacciones."
        }
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refined_story": "Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a los servicios y funciones disponibles en mi perfil personal, como la gestión de información personal y el acceso a contenido específico.",
                "session_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )

@router.post(
    "/refine_story",
    response_model=RefineStoryResponse,
    summary="Refina una historia de usuario manteniendo el contexto",
    tags=["Refinement"]
)
async def refine_story(request: RefineStoryRequest):
    """
    Refinar una historia de usuario para mejorar su claridad y completitud, manteniendo el contexto de la conversación.
    
    - **story**: Historia de usuario en formato de texto.
    - **session_id**: (Opcional) Identificador de la sesión para mantener el contexto.
    """
    try:
        session_id = str(request.session_id) if request.session_id else str(uuid4())
        
        # Refina la historia con el contexto de la sesión
        refined_story = await llm_service.refine_story_with_context(request.story, session_id)
        
        return {"refined_story": refined_story, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
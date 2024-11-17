from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from src.llm.service import LLMService
from src.llm.config import get_llm_config

router = APIRouter()
llm_service = LLMService(get_llm_config())

class RefineStoryRequest(BaseModel):
    story: str = Field(
        ...,
        json_schema_extra={
            "example": "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal.",
            "description": "Descripción detallada de la historia de usuario que desea refinar."
        }
    )
    feedback: str | None = Field(
        None,
        json_schema_extra={
            "example": "La historia debería especificar el método de autenticación y los datos a los que se accederá.",
            "description": "Feedback opcional del usuario sobre la historia refinada anterior."
        }
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "story": "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal.",
                "feedback": "La historia debería especificar el método de autenticación y los datos a los que se accederá."
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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refined_story": "Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a los servicios y funciones disponibles en mi perfil personal, como la gestión de información personal y el acceso a contenido específico."
            }
        }
    )

@router.post(
    "/refine_story",
    response_model=RefineStoryResponse,
    summary="Refina una historia de usuario",
    tags=["Refinement"]
)
async def refine_story(request: RefineStoryRequest):
    """
    Refinar una historia de usuario para mejorar su claridad y completitud.

    - **story**: Historia de usuario en formato de texto.
    - **feedback**: Feedback opcional del usuario sobre la historia refinada anterior.
    """
    try:
        refined_story = await llm_service.refine_story(request.story, request.feedback)
        return {"refined_story": refined_story}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
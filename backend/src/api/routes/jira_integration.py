from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, model_validator, ValidationError
from atlassian import Jira
import os
import re
import logging
from typing import Optional, Literal

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter()

class JiraStoryResponse(BaseModel):
    """Modelo de respuesta para obtener una historia de Jira"""
    title: str
    description: Optional[str] = None

class JiraStoryUpdateRequest(BaseModel):
    """Modelo para solicitar la actualización de una historia de usuario"""
    title: str = Field(..., min_length=1, max_length=255, description="Título de la historia de usuario")
    description: Optional[str] = Field(None, description="Descripción de la historia de usuario")
    story_id: Optional[str] = Field(None, description="ID de la historia en Jira (si ya existe)")

    @model_validator(mode='after')
    def validate_story_id(self) -> 'JiraStoryUpdateRequest':
        if self.story_id is not None:
            if not re.match(r'^[A-Z]+-\d+$', self.story_id):
                raise HTTPException(
                    status_code=400,
                    detail="ID de historia inválido. Debe tener el formato PROYECTO-123"
                )
        return self

class JiraStoryUpdateResponse(BaseModel):
    """Modelo de respuesta para la actualización de historia de usuario"""
    story_id: str
    action: Literal["created", "updated"]
    message: str

@router.post("/jira/story", response_model=JiraStoryUpdateResponse)
async def update_or_create_jira_story(
    story_request: JiraStoryUpdateRequest,
):
    """
    Actualizar una historia de usuario en Jira o crear una nueva si no existe.
    
    - Si se proporciona `story_id`, intenta actualizar la historia existente.
    - Si no se proporciona `story_id`, intenta crear una nueva historia.
    """
    # Verificar variables de entorno
    if not os.getenv('JIRA_URL') or not os.getenv('JIRA_TOKEN') or not os.getenv('JIRA_PROJECT_KEY'):
        raise HTTPException(
            status_code=500,
            detail="Error al conectar con Jira: Configuración incompleta. Asegúrese de definir JIRA_URL, JIRA_TOKEN y JIRA_PROJECT_KEY"
        )

    try:
        # Inicializar cliente de Jira
        jira = Jira(
            url=os.getenv('JIRA_URL'),
            token=os.getenv('JIRA_TOKEN')
        )

        # Intentar actualizar o crear la historia
        try:
            if story_request.story_id:
                # Actualizar historia existente
                # Usar fields para actualizar título y descripción
                logger.info(f"Intentando actualizar historia: {story_request.story_id}")
                try:
                    jira.update_issue_field(
                        story_request.story_id, 
                        fields={
                            'summary': story_request.title,
                            'description': story_request.description or ''
                        }
                    )
                except Exception as update_error:
                    logger.error(f"Error al actualizar historia: {update_error}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error al actualizar historia: {str(update_error)}"
                    )

                return JiraStoryUpdateResponse(
                    story_id=story_request.story_id,
                    action="updated",
                    message="Historia actualizada exitosamente"
                )
            else:
                # Crear nueva historia
                logger.info(f"Intentando crear nueva historia en proyecto: {os.getenv('JIRA_PROJECT_KEY')}")
                try:
                    logger.info(f"Datos de la solicitud: {story_request}")
                    
                    # Inspeccionar métodos disponibles
                    logger.info(f"Métodos disponibles en Jira: {dir(jira)}")
                    
                    try:
                        # Intentar método de la biblioteca Atlassian
                        # Imprimir todos los argumentos posibles
                        logger.info("Argumentos disponibles:")
                        for method in dir(jira):
                            if 'issue' in method.lower():
                                logger.info(f"Método relacionado: {method}")
                        
                        # Intentar con diferentes formatos
                        new_issue = jira.create_issue(
                            fields={
                                'project': {'key': os.getenv('JIRA_PROJECT_KEY')},
                                'summary': story_request.title,
                                'description': story_request.description or '',
                                'issuetype': {'name': 'Story'}
                            }
                        )
                    except Exception as create_error:
                        logger.error(f"Error detallado al crear historia: {create_error}")
                        logger.error(f"Tipo de error: {type(create_error)}")
                        logger.error(f"Argumentos del error: {create_error.args}")
                        raise

                    return JiraStoryUpdateResponse(
                        story_id=new_issue['key'],
                        action="created",
                        message="Historia creada exitosamente"
                    )
                except Exception as e:
                    logger.error(f"Error inesperado al crear historia: {e}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error al crear historia: {str(e)}"
                    )

        except Exception as e:
            logger.error(f"Error inesperado al procesar solicitud: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error inesperado al procesar la solicitud: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado al procesar la solicitud: {str(e)}"
        )

# Endpoint existente para obtener historia de Jira
@router.get("/jira/story/{story_id}", response_model=JiraStoryResponse)
async def get_jira_story(
    story_id: str,
):
    """
    Obtener una historia de usuario desde Jira.
    
    - **story_id**: ID de la historia en Jira (ejemplo: STORYASIS-1)
    """
    # Validar formato del ID
    if not re.match(r'^[A-Z]+-\d+$', story_id):
        raise HTTPException(status_code=404, detail="ID de historia inválido")

    # Verificar variables de entorno
    if not os.getenv('JIRA_URL') or not os.getenv('JIRA_TOKEN'):
        raise HTTPException(
            status_code=500,
            detail="Error al conectar con Jira: Configuración incompleta"
        )

    try:
        # Inicializar cliente de Jira
        jira = Jira(
            url=os.getenv('JIRA_URL'),
            token=os.getenv('JIRA_TOKEN')
        )

        # Obtener la historia
        try:
            issue = jira.issue(story_id)
        except Exception as e:
            if "Issue Does Not Exist" in str(e):
                raise HTTPException(status_code=404, detail="Historia no encontrada")
            raise HTTPException(
                status_code=500,
                detail=f"Error al conectar con Jira: {str(e)}"
            )

        if not issue or 'fields' not in issue:
            raise HTTPException(status_code=404, detail="Historia no encontrada")

        # Extraer título y descripción
        summary = issue['fields'].get('summary')
        if not summary:
            raise HTTPException(
                status_code=500,
                detail="Error: La historia no tiene título"
            )

        # Crear la respuesta con los datos de Jira
        return JiraStoryResponse(
            title=summary,
            description=issue['fields'].get('description', '')
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener la historia: {str(e)}"
        )

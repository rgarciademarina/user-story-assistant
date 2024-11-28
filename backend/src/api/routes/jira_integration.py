from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from atlassian import Jira
import os
import re
from typing import Optional

router = APIRouter()

class JiraStoryResponse(BaseModel):
    title: str = Field(
        ...,
        description="Título de la historia de usuario en Jira"
    )
    description: Optional[str] = Field(
        None,
        description="Descripción de la historia de usuario en Jira"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "STORYASIS-1: Implementar login de usuario",
                "description": "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal"
            }
        }
    )

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

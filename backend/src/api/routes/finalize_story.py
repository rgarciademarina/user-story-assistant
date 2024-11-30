from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict, ValidationInfo, field_validator
from typing import Optional, List
from src.dependencies import get_llm_service
from src.llm.service import LLMService
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class FinalizeStoryRequest(BaseModel):
    """
    Modelo para la solicitud de finalización de historia de usuario.
    Puede recibir una historia refinada + casos esquina + estrategia de testing,
    o una historia ya finalizada para iteración.
    """
    model_config = ConfigDict(extra='forbid')
    
    session_id: Optional[UUID] = Field(
        None,
        description="ID de sesión para mantener el contexto de la conversación. Si no se proporciona, se creará una nueva sesión.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    
    # Primera opción: Historia refinada + casos + estrategia
    refined_story: Optional[str] = Field(
        None,
        description="Historia de usuario refinada",
        example="Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura."
    )
    corner_cases: Optional[List[str]] = Field(
        None,
        description="Lista de casos esquina identificados",
        example=[
            "Intentos de inicio de sesión con credenciales incorrectas",
            "Bloqueo de cuenta por múltiples intentos fallidos",
            "Acceso simultáneo desde múltiples dispositivos"
        ]
    )
    testing_strategy: Optional[List[str]] = Field(
        None,
        description="Lista de estrategias de prueba",
        example=[
            "Pruebas unitarias para la validación de credenciales",
            "Pruebas de integración para el proceso de autenticación",
            "Pruebas de seguridad para intentos de acceso no autorizado"
        ]
    )
    
    # Segunda opción: Historia finalizada para iteración
    finalized_story: Optional[str] = Field(
        None,
        description="Historia de usuario finalizada para iterar sobre ella",
        example="""Historia Principal:
Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura.

Criterios de Aceptación Funcionales:
Given un usuario registrado
When intenta iniciar sesión con credenciales correctas
Then debe obtener acceso a su cuenta
And ver sus datos personales

Given un usuario
When intenta iniciar sesión con credenciales incorrectas
Then debe recibir un mensaje de error
And se debe registrar el intento fallido

Tests Funcionales:
Given un usuario bloqueado por múltiples intentos fallidos
When intenta iniciar sesión con credenciales correctas
Then debe recibir un mensaje indicando que su cuenta está bloqueada
And debe proporcionarse instrucciones para desbloquear la cuenta

Criterios de Aceptación de Testing:
1. Implementar pruebas unitarias para la validación de credenciales
2. Realizar pruebas de integración del flujo completo de autenticación
3. Ejecutar pruebas de seguridad para verificar la protección contra accesos no autorizados"""
    )
    feedback: Optional[str] = Field(
        None,
        description="Feedback opcional para mejorar la historia",
        example="Por favor, añadir más criterios relacionados con la recuperación de contraseña y la autenticación de dos factores."
    )
    format_preferences: Optional[dict] = Field(
        None,
        description="Preferencias de formato para la salida",
        example={
            "acceptance_criteria_format": "gherkin",
            "functional_tests_format": "gherkin"
        }
    )

    @field_validator('refined_story', 'corner_cases', 'testing_strategy', 'finalized_story')
    def validate_input_combination(cls, v, info: ValidationInfo):
        values = info.data
        field = info.field_name
        # Si es el campo finalized_story
        if field == 'finalized_story':
            if v is not None and any([
                values.get('refined_story'),
                values.get('corner_cases'),
                values.get('testing_strategy')
            ]):
                raise ValueError(
                    "No puedes proporcionar una historia finalizada junto con los componentes individuales. "
                    "Proporciona solo la historia finalizada O los componentes individuales."
                )
        # Si es cualquier otro campo
        else:
            if values.get('finalized_story') is not None:
                raise ValueError(
                    "No puedes proporcionar componentes individuales cuando ya has proporcionado una historia finalizada. "
                    "Proporciona solo la historia finalizada O los componentes individuales."
                )
            elif field == 'refined_story' and v is None and not values.get('finalized_story'):
                raise ValueError("Debes proporcionar una historia refinada cuando no proporcionas una historia finalizada")
            elif field == 'corner_cases' and v is None and not values.get('finalized_story'):
                raise ValueError("Debes proporcionar casos esquina cuando no proporcionas una historia finalizada")
            elif field == 'testing_strategy' and v is None and not values.get('finalized_story'):
                raise ValueError("Debes proporcionar estrategia de testing cuando no proporcionas una historia finalizada")
        return v

class FinalizeStoryResponse(BaseModel):
    """Modelo para la respuesta de finalización de historia de usuario"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "finalized_story": """Historia Principal:
Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura.

Criterios de Aceptación Funcionales:
Given un usuario registrado
When intenta iniciar sesión con credenciales correctas
Then debe obtener acceso a su cuenta
And ver sus datos personales

Given un usuario
When intenta recuperar su contraseña
Then debe recibir un enlace de recuperación por correo
And el enlace debe expirar después de 24 horas

Tests Funcionales:
Given un usuario con autenticación de dos factores activada
When inicia sesión con credenciales correctas
Then debe solicitarse el código de verificación
And debe validarse el código antes de permitir el acceso

Criterios de Aceptación de Testing:
1. Implementar pruebas unitarias para validación de credenciales y 2FA
2. Realizar pruebas de integración del flujo completo
3. Ejecutar pruebas de seguridad y penetración""",
                "feedback": "Se han añadido criterios de aceptación y tests para la recuperación de contraseña y autenticación de dos factores según el feedback proporcionado."
            }
        }
    )
    
    session_id: UUID = Field(..., description="ID de la sesión")
    finalized_story: str = Field(..., description="Historia de usuario finalizada")
    feedback: str = Field(..., description="Feedback sobre los cambios y decisiones tomadas")

@router.post(
    "/finalize_story",
    response_model=FinalizeStoryResponse,
    summary="Finaliza una historia de usuario",
    tags=["Finalization"]
)
async def finalize_story(
    request: FinalizeStoryRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Finaliza una historia de usuario integrando todos sus componentes.

    - Si se proporciona una historia refinada + casos esquina + estrategia de testing:
      Integra todos los componentes en una historia finalizada.
    
    - Si se proporciona una historia finalizada:
      Procesa el feedback y mejora la historia existente.

    La historia finalizada incluirá:
    - Historia Principal
    - Criterios de Aceptación Funcionales (formato configurable, Gherkin por defecto)
    - Tests Funcionales (formato configurable, Gherkin por defecto)
    - Criterios de Aceptación de Testing
    """
    try:
        session_id = request.session_id or llm_service.create_session()

        # Determinar el input principal basado en el tipo de solicitud
        story_input = request.finalized_story if request.finalized_story else request.refined_story

        result = await llm_service.finalize_story(
            session_id=session_id,
            story_input=story_input,
            corner_cases=request.corner_cases,
            testing_strategy=request.testing_strategy,
            feedback=request.feedback,
            format_preferences=request.format_preferences
        )

        return {
            "session_id": session_id,
            "finalized_story": result['finalized_story'],
            "feedback": result['feedback']
        }
    except Exception as e:
        logger.error(f"Error al finalizar la historia: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

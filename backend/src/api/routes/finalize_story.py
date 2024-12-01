from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict, ValidationInfo, field_validator, model_validator
from typing import Optional, List
from src.dependencies import get_llm_service
from src.llm.service import LLMService
from uuid import UUID
import logging
import uuid

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
        json_schema_extra={
            "example": "123e4567-e89b-12d3-a456-426614174000"
        }
    )
    
    # Primera opción: Historia refinada + casos + estrategia
    refined_story: Optional[str] = Field(
        None,
        description="Historia de usuario refinada",
        json_schema_extra={
            "example": "Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura."
        }
    )
    corner_cases: Optional[List[str]] = Field(
        None,
        description="Lista de casos esquina identificados",
        json_schema_extra={
            "example": [
                "Intentos de inicio de sesión con credenciales incorrectas",
                "Bloqueo de cuenta por múltiples intentos fallidos",
                "Acceso simultáneo desde múltiples dispositivos"
            ]
        }
    )
    testing_strategy: Optional[List[str]] = Field(
        None,
        description="Lista de estrategias de prueba",
        json_schema_extra={
            "example": [
                "Pruebas unitarias para la validación de credenciales",
                "Pruebas de integración para el proceso de autenticación",
                "Pruebas de seguridad para intentos de acceso no autorizado"
            ]
        }
    )
    
    # Segunda opción: Historia finalizada para iteración
    finalized_story: Optional[str] = Field(
        None,
        description="Historia de usuario finalizada para iterar sobre ella",
        json_schema_extra={
            "example": """Historia Principal:
Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura.

Criterios de Aceptación Funcionales:
Dado un usuario registrado
Cuando intenta iniciar sesión con credenciales correctas
Entonces debe obtener acceso a su cuenta
Y ver sus datos personales

Dado un usuario
Cuando intenta iniciar sesión con credenciales incorrectas
Entonces debe recibir un mensaje de error
Y se debe registrar el intento fallido

Tests Funcionales:
Dado un usuario bloqueado por múltiples intentos fallidos
Cuando intenta iniciar sesión con credenciales correctas
Entonces debe recibir un mensaje indicando que su cuenta está bloqueada
Y debe proporcionarse instrucciones para desbloquear la cuenta

Criterios de Aceptación de Testing:
1. Implementar pruebas unitarias para la validación de credenciales y 2FA
2. Realizar pruebas de integración del flujo completo
3. Ejecutar pruebas de seguridad y penetración""",
            "example": "Por favor, añadir más criterios relacionados con la recuperación de contraseña y la autenticación de dos factores."
        }
    )
    feedback: Optional[str] = Field(
        None,
        description="Feedback opcional para mejorar la historia",
        json_schema_extra={
            "example": "Por favor, añadir más criterios relacionados con la recuperación de contraseña y la autenticación de dos factores."
        }
    )
    format_preferences: Optional[dict] = Field(
        None,
        description="Preferencias de formato para la salida",
        json_schema_extra={
            "example": {
                "acceptance_criteria_format": "gherkin",
                "functional_tests_format": "gherkin"
            }
        }
    )

    @model_validator(mode='after')
    def validate_input_combination(self) -> 'FinalizeStoryRequest':
        # Si tenemos una historia finalizada, no podemos tener componentes individuales
        if self.finalized_story is not None and any([
            self.refined_story,
            self.corner_cases,
            self.testing_strategy
        ]):
            raise ValueError(
                "No puedes proporcionar una historia finalizada junto con los componentes individuales. "
                "Proporciona solo la historia finalizada O los componentes individuales."
            )
        
        # Si no tenemos historia finalizada, necesitamos todos los componentes
        if self.finalized_story is None:
            if self.refined_story is None:
                raise ValueError("Debes proporcionar una historia refinada cuando no proporcionas una historia finalizada")
            if self.corner_cases is None:
                raise ValueError("Debes proporcionar casos esquina cuando no proporcionas una historia finalizada")
            if self.testing_strategy is None:
                raise ValueError("Debes proporcionar estrategia de testing cuando no proporcionas una historia finalizada")
        
        return self

class FinalizeStoryResponse(BaseModel):
    """Modelo para la respuesta de finalización de historia de usuario"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "finalized_story": """Historia Principal:
Como usuario registrado, quiero poder iniciar sesión en mi cuenta usando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura.

Criterios de Aceptación Funcionales:
Dado un usuario registrado
Cuando intenta iniciar sesión con credenciales correctas
Entonces debe obtener acceso a su cuenta
Y ver sus datos personales

Dado un usuario
Cuando intenta recuperar su contraseña
Entonces debe recibir un enlace de recuperación por correo
Y el enlace debe expirar después de 24 horas

Tests Funcionales:
Dado un usuario con autenticación de dos factores activada
Cuando inicia sesión con credenciales correctas
Entonces debe solicitarse el código de verificación
Y debe validarse el código antes de permitir el acceso

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
    # Log the input details with more verbosity
    logger.info("Finalize Story Request Details:")
    logger.info(f"Session ID: {request.session_id}")
    logger.info(f"Refined Story: {request.refined_story}")
    logger.info(f"Corner Cases: {request.corner_cases}")
    logger.info(f"Testing Strategy: {request.testing_strategy}")
    logger.info(f"Feedback: {request.feedback}")

    try:
        # Convert session_id to UUID, creating a new one if not provided
        if request.session_id:
            try:
                session_id = UUID(str(request.session_id))
            except ValueError:
                logger.warning(f"Invalid session_id format: {request.session_id}. Generating new UUID.")
                session_id = uuid.uuid4()
        else:
            session_id = uuid.uuid4()

        # Call LLM service to finalize the story
        response = await llm_service.finalize_story(
            session_id=session_id,
            story_input=request.refined_story or request.finalized_story,
            corner_cases=request.corner_cases,
            testing_strategy=request.testing_strategy,
            feedback=request.feedback
        )

        # Log the full LLM response for debugging
        logger.info("Full LLM Response:")
        logger.info(str(response))

        # Extract the finalized story from the response dictionary
        finalized_story = response.get('finalized_story', '')
        feedback = response.get('feedback', '')

        # Detailed logging for functional tests section
        logger.info("Searching for Functional Tests Section:")
        
        # Explicitly log the entire finalized story for inspection
        logger.info("Full Finalized Story:")
        logger.info(finalized_story)

        # Check for Functional Tests section
        tests_section_start = finalized_story.find("#### Tests Funcionales")
        logger.info(f"Tests Section Start Index: {tests_section_start}")

        # If Tests Funcionales section exists
        if tests_section_start != -1:
            # Try to extract the tests section
            tests_section_end = finalized_story.find("#### Conclusiones", tests_section_start)
            if tests_section_end == -1:
                tests_section_end = len(finalized_story)
            
            tests_section = finalized_story[tests_section_start:tests_section_end]
            logger.info("Functional Tests Section Found:")
            logger.info(tests_section)
            
            # Detailed test extraction
            test_pattern = r"#### Test \d+ - .*"
            import re
            test_matches = re.findall(test_pattern, tests_section, re.MULTILINE)
            
            logger.info("Detailed Test Extraction:")
            logger.info(f"Number of Tests Found: {len(test_matches)}")
            for test in test_matches:
                logger.info(test)
            
            # Log if no tests are found, but don't raise an exception
            if len(test_matches) == 0:
                logger.warning("No functional tests found in the Tests Funcionales section.")
        else:
            # No Tests Funcionales section found
            logger.warning("NO 'Tests Funcionales' SECTION FOUND IN THE RESPONSE!")

        # Create and return the response
        finalized_story_response = FinalizeStoryResponse(
            session_id=session_id,
            finalized_story=finalized_story,
            feedback=feedback
        )

        return finalized_story_response

    except Exception as e:
        logger.error(f"Error in finalize_story: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

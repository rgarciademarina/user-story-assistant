from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.schema import LLMResult, Generation
from typing import Any, List, Optional, Dict, Union
from src.llm.service import LLMService
from uuid import UUID, uuid4

class MockOllamaLLM(LLM):
    """Mock para OllamaLLM que retorna respuestas predefinidas"""

    def __init__(self):
        """Inicializar el mock LLM"""
        super().__init__()
        print("[MockOllamaLLM] Inicializando mock LLM")

    @property
    def _llm_type(self) -> str:
        """Retorna el tipo de LLM"""
        return "mock_ollama"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Procesar una llamada al LLM"""
        return self._get_mock_response(prompt)

    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Procesar una llamada asíncrona al LLM"""
        return self._get_mock_response(prompt)

    async def _agenerate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generar respuestas para múltiples prompts de forma asíncrona"""
        generations = []
        for prompt in prompts:
            response = self._get_mock_response(prompt)
            generations.append([Generation(text=response)])
        return LLMResult(generations=generations)

    def _get_mock_response(self, prompt: str) -> str:
        """Obtener una respuesta mock basada en el prompt"""
        print(f"[MockOllamaLLM] Procesando prompt: {prompt}")
        
        # Respuesta para refinar historia
        if "historia de usuario" in prompt.lower() and "refina la historia" in prompt.lower():
            return """**Historia Refinada:**
Como usuario registrado, quiero poder iniciar sesión en mi cuenta utilizando mi correo electrónico y contraseña para acceder a mis datos personales de manera segura.

**Cambios Realizados:**
- Se especificó el tipo de usuario (registrado)
- Se añadió el método de autenticación (correo y contraseña)
- Se clarificó el propósito (acceso seguro a datos personales)"""
        
        # Respuesta para casos esquina
        elif "casos esquina" in prompt.lower() and "actualiza y mejora la lista de casos esquina" in prompt.lower():
            return """**Casos Esquina Actualizados:**
1. **Intentos de Inicio de Sesión Fallidos:** El usuario ingresa una contraseña incorrecta repetidamente.
2. **Acceso desde Ubicaciones No Reconocidas:** Intentos de inicio de sesión desde ubicaciones geográficas inusuales.
3. **Bloqueo por Inactividad:** La sesión expira después de un período sin actividad."""

        # Respuesta para estrategias de testing
        elif "estrategias de testing" in prompt.lower() and "actualiza y mejora la lista de estrategias de testing" in prompt.lower():
            return """**Estrategias de Testing Actualizadas:**
1. **Pruebas de Autenticación:** Verificar el proceso de inicio de sesión con diferentes credenciales.
2. **Pruebas de Seguridad:** Validar el manejo de sesiones y tokens de acceso.
3. **Pruebas de Rendimiento:** Evaluar el sistema bajo carga de múltiples inicios de sesión simultáneos."""

        else:
            print("[MockOllamaLLM] ¡ADVERTENCIA! No se encontró un caso que coincida con el prompt")
            print(f"[MockOllamaLLM] Prompt recibido: {prompt[:200]}...")
            return "Respuesta mock genérica"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {"mock_type": "ollama"}

    def bind(self, **kwargs: Any) -> "MockOllamaLLM":
        """Bind arguments to the LLM."""
        return self

    async def abatch(self, prompts: List[str], **kwargs: Any) -> List[str]:
        """Batch process prompts."""
        return [self._get_mock_response(prompt) for prompt in prompts]

    async def ainvoke(
        self,
        input: Union[str, List[str]],
        config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[str, List[str]]:
        """Invoke the LLM asynchronously."""
        if isinstance(input, str):
            response = self._get_mock_response(input)
            print(f"[MockOllamaLLM] Respuesta: {response}")
            return response
        elif isinstance(input, list):
            responses = [self._get_mock_response(prompt) for prompt in input]
            print(f"[MockOllamaLLM] Respuestas: {responses}")
            return responses
        else:
            raise ValueError(f"Input type {type(input)} not supported")

class MockLLMService(LLMService):
    """Mock del servicio LLM para pruebas"""

    def __init__(self):
        """Inicializar el servicio mock"""
        self._mock_llm = MockOllamaLLM()
        self._sessions = {}

    def create_session(self) -> UUID:
        """Crear una nueva sesión"""
        session_id = uuid4()
        self._sessions[session_id] = {"history": []}
        return session_id

    async def refine_story(
        self,
        session_id: UUID,
        user_story: str,
        feedback: Optional[str] = None
    ) -> Dict[str, str]:
        """Mock para refinar una historia de usuario"""
        prompt = f"Refina la historia de usuario: {user_story}"
        if feedback:
            prompt += f"\nFeedback: {feedback}"
        
        response = await self._mock_llm._acall(prompt)
        return {
            "refined_story": response,
            "refinement_feedback": "Feedback mock del refinamiento"
        }

    async def identify_corner_cases(
        self,
        session_id: UUID,
        refined_story: str,
        feedback: Optional[str] = None,
        existing_corner_cases: Optional[List[str]] = None
    ) -> Dict[str, Union[List[str], str]]:
        """Mock para identificar casos esquina"""
        prompt = f"Analiza los casos esquina para la historia: {refined_story}"
        if feedback:
            prompt += f"\nFeedback: {feedback}"
        if existing_corner_cases:
            prompt += f"\nCasos existentes: {existing_corner_cases}"
        
        response = await self._mock_llm._acall(prompt)
        
        # Generar casos esquina realistas
        corner_cases = [
            "1. **Intentos de Inicio de Sesión Fallidos:** El usuario ingresa una contraseña incorrecta repetidamente.",
            "2. **Acceso desde Ubicaciones No Reconocidas:** Intentos de inicio de sesión desde ubicaciones geográficas inusuales.",
            "3. **Bloqueo por Inactividad:** La sesión expira después de un período sin actividad.",
            "4. **Fuerza Bruta:** Intentos automatizados de acceso usando diccionarios de contraseñas."
        ]
        
        return {
            "corner_cases": corner_cases,
            "corner_cases_feedback": "Se han identificado casos esquina relacionados con seguridad, autenticación y manejo de sesiones."
        }

    async def propose_testing_strategy(
        self,
        session_id: UUID,
        refined_story: str,
        corner_cases: List[str],
        feedback: Optional[str] = None,
        existing_testing_strategies: Optional[List[str]] = None
    ) -> Dict[str, Union[List[str], str]]:
        """Mock para proponer estrategias de testing"""
        prompt = f"Propón estrategias de testing para la historia: {refined_story}"
        if feedback:
            prompt += f"\nFeedback: {feedback}"
        if existing_testing_strategies:
            prompt += f"\nEstrategias existentes: {existing_testing_strategies}"
        
        response = await self._mock_llm._acall(prompt)
        
        # Generar estrategias de prueba realistas
        strategies = [
            "1. **Pruebas de Autenticación:** Verificar el proceso de inicio de sesión con credenciales válidas e inválidas.",
            "2. **Pruebas de Seguridad:** Validar la protección contra accesos no autorizados y ataques de fuerza bruta.",
            "3. **Pruebas de Manejo de Sesiones:** Comprobar el control de acceso y expiración de sesiones por inactividad.",
            "4. **Pruebas de Rendimiento:** Evaluar el sistema bajo carga con múltiples autenticaciones simultáneas."
        ]

        if feedback and "integración" in feedback.lower():
            strategies.append("5. **Pruebas de Integración:** Verificar la integración correcta con el sistema de autenticación y servicios externos.")
        
        return {
            "testing_strategies": strategies,
            "testing_feedback": "Se han definido estrategias que cubren aspectos de seguridad, rendimiento y funcionalidad del sistema."
        }

    async def finalize_story(
        self,
        session_id: Optional[UUID],
        story_input: Optional[str] = None,
        corner_cases: Optional[List[str]] = None,
        testing_strategy: Optional[List[str]] = None,
        feedback: Optional[str] = None,
        format_preferences: Optional[Dict[str, str]] = None
    ) -> Dict[str, Union[str, List[str]]]:
        """Mock para finalizar una historia de usuario"""
        # Si tenemos corner_cases y testing_strategy, es una solicitud con componentes individuales
        if corner_cases and testing_strategy:
            return {
                "finalized_story": """Historia Principal:
Como usuario registrado quiero iniciar sesión con email y contraseña

Criterios de Aceptación:
Given un usuario registrado
When intenta iniciar sesión con credenciales correctas
Then debe obtener acceso a su cuenta

Given credenciales inválidas
When intenta iniciar sesión múltiples veces
Then debe bloquear la cuenta temporalmente""",
                "feedback": "Se ha generado una historia completa integrando los casos esquina y estrategias de testing proporcionados.",
                "acceptance_criteria": [
                    "Given un usuario registrado When intenta iniciar sesión Then debe validar sus credenciales",
                    "Given múltiples intentos fallidos When excede el límite Then debe bloquear la cuenta"
                ],
                "functional_tests": [
                    "test_login_with_valid_credentials",
                    "test_account_lockout_after_failed_attempts"
                ]
            }
        else:
            # Si solo tenemos story_input y feedback, es una iteración sobre una historia existente
            return {
                "finalized_story": """Historia Principal:
Como usuario registrado quiero iniciar sesión con email y contraseña

Criterios de Aceptación:
Given un usuario registrado
When intenta iniciar sesión con credenciales correctas
Then debe obtener acceso a su cuenta

Given un usuario registrado
When habilita la autenticación de dos factores
Then debe recibir un código por SMS para completar el inicio de sesión""",
                "feedback": "Se han añadido criterios para autenticación de dos factores según el feedback.",
                "acceptance_criteria": [
                    "Given un usuario registrado When intenta iniciar sesión Then debe validar sus credenciales",
                    "Given credenciales válidas When se habilita 2FA Then debe enviar código por SMS"
                ],
                "functional_tests": [
                    "test_login_with_valid_credentials",
                    "test_two_factor_authentication"
                ]
            }

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.schema import LLMResult, Generation
from typing import Any, List, Optional, Dict, Union

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
3. **Bloqueo por Inactividad:** La sesión expira después de un período sin actividad.

**Análisis de Cambios:**
Los casos cubren escenarios críticos de seguridad, autenticación y manejo de sesiones."""
        
        # Respuesta para estrategias de testing
        elif "estrategias de testing" in prompt.lower() and "actualiza y mejora la lista de estrategias de testing" in prompt.lower():
            return """**Estrategias de Testing Actualizadas:**
1. **Pruebas de Autenticación:** Verificar el proceso de inicio de sesión con diferentes credenciales.
2. **Pruebas de Seguridad:** Validar el manejo de sesiones y tokens de acceso.
3. **Pruebas de Rendimiento:** Evaluar el sistema bajo carga de múltiples inicios de sesión simultáneos.

**Análisis de Cambios:**
Las pruebas cubren aspectos esenciales de autenticación, seguridad y rendimiento."""
        
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

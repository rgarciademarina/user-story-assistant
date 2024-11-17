from .service import LLMService
from .config import get_llm_config

# Inicializar LLMService con la configuración
llm_service = LLMService(config=get_llm_config())

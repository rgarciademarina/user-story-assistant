from fastapi import Depends
from src.llm.service import LLMService
from src.llm.instance import llm_service

_llm_service_instance = None

def get_llm_service() -> LLMService:
    """
    Dependency provider for LLM service.
    """
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = llm_service
    return _llm_service_instance

def override_llm_service(service: LLMService):
    """
    Override the LLM service instance for testing.
    """
    global _llm_service_instance
    _llm_service_instance = service

"""Módulo para mantener una única instancia del servicio LLM."""

from src.llm.service import LLMService
from src.llm.config import get_llm_config

# Crear una única instancia del servicio LLM
llm_service = LLMService(get_llm_config())

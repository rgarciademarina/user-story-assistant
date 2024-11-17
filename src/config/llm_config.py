from dataclasses import dataclass
from langchain_ollama import OllamaLLM

@dataclass
class LLMConfig:
    llm: OllamaLLM
    refinement_prompt_template: str
    corner_case_prompt_template: str
    testing_strategy_prompt_template: str
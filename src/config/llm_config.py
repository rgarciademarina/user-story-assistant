from dataclasses import dataclass
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

@dataclass
class LLMConfig:
    llm: ChatOpenAI
    refinement_prompt_template: str
    corner_case_prompt_template: str
    testing_strategy_prompt_template: str
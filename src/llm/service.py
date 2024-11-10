import json
import logging
from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .config import LLMConfig, get_llm_config

# Configuración del logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class LLMService:
    def __init__(self, config: LLMConfig = None):
        self.config = config or get_llm_config()
        self.llm = Ollama(
            model=self.config.MODEL_NAME,
            base_url=self.config.OLLAMA_BASE_URL,
            temperature=self.config.TEMPERATURE
        )
        
        # Template simplificado con llaves escapadas y instrucciones claras
        template = """Analiza esta historia de usuario: {story}

Proporciona un análisis en formato JSON con esta estructura exacta:
{{
    "improvements": ["mejora1", "mejora2"],
    "edge_cases": ["caso1", "caso2"],
    "testing_strategies": ["estrategia1", "estrategia2"]
}}

**Responde únicamente con el bloque JSON sin ningún texto adicional.**"""
        
        self.prompt = PromptTemplate.from_template(template)
        
        # Pipeline utilizando JsonOutputParser para manejar automáticamente la respuesta JSON
        self.chain = self.prompt | self.llm | JsonOutputParser()

    async def analyze_user_story(self, user_story: str) -> dict:
        """
        Analiza una historia de usuario y proporciona recomendaciones.
        
        Args:
            user_story: El texto de la historia de usuario a analizar.
            
        Returns:
            dict: Diccionario con mejoras, casos esquina y estrategias de testing.
        """
        try:
            # Obtener respuesta ya parseada como dict
            response = await self.chain.ainvoke({"story": user_story})
            logger.info(f"Respuesta recibida del LLM: {response}")
            return response
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear la respuesta JSON: {str(e)}")
            raise Exception(f"Error al parsear la respuesta JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Error al analizar la historia de usuario: {str(e)}")
            raise Exception(f"Error al analizar la historia de usuario: {str(e)}")

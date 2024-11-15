from fastapi import FastAPI
from src.api.routes.refine_story import router as refine_story_router
from src.api.routes.identify_corner_cases import router as identify_corner_cases_router
from src.api.routes.propose_testing_strategy import router as propose_testing_strategy_router
from src.llm.config import get_llm_config
from src.llm.service import LLMService

app = FastAPI(
    title="Asistente de Refinamiento de Historias de Usuario",
    version="1.0.0",
    description="Una API para refinar historias de usuario, identificar casos esquina y proponer estrategias de testing utilizando un modelo LLM."
)

# Inicializar LLMService con la configuración
llm_service = LLMService(config=get_llm_config())

# Incluir los routers separados
app.include_router(refine_story_router)
app.include_router(identify_corner_cases_router)
app.include_router(propose_testing_strategy_router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido al Asistente de Refinamiento de Historias de Usuario"}

# Ruta de depuración para verificar la configuración
@app.get("/debug/config")
def debug_config():
    config = get_llm_config()
    return config.dict()

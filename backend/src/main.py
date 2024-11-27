from fastapi import FastAPI
from src.api.routes.refine_story import router as refine_story_router
from src.api.routes.identify_corner_cases import router as identify_corner_cases_router
from src.api.routes.propose_testing_strategy import router as propose_testing_strategy_router
from src.llm.config import get_llm_config


app = FastAPI(
    title="User Story Assistant",
    description="API para asistir en la creación y refinamiento de historias de usuario",
    version="1.0.0"
)

app.include_router(refine_story_router, prefix="/api/v1")
app.include_router(identify_corner_cases_router, prefix="/api/v1")
app.include_router(propose_testing_strategy_router, prefix="/api/v1")

@app.get("/")
async def read_root():
    return {"message": "Bienvenido al Asistente de Refinamiento de Historias de Usuario"}

# Ruta de depuración para verificar la configuración
@app.get("/debug/config")
async def debug_config():
    config = get_llm_config()
    return config.model_dump()

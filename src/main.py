from fastapi import FastAPI
from src.api.routes.refine_story import router as refine_story_router
from src.api.routes.identify_corner_cases import router as identify_corner_cases_router
from src.api.routes.propose_testing_strategy import router as propose_testing_strategy_router

app = FastAPI(
    title="Asistente de Refinamiento de Historias de Usuario",
    version="1.0.0",
    description="Una API para refinar historias de usuario, identificar casos esquina y proponer estrategias de testing utilizando un modelo LLM."
)

# Incluir los routers separados
app.include_router(refine_story_router)
app.include_router(identify_corner_cases_router)
app.include_router(propose_testing_strategy_router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido al Asistente de Refinamiento de Historias de Usuario"}

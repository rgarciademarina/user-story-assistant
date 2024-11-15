from langflow import App, Step, TextOutput, Confirmation
from src.llm.service import LLMService
from src.llm.config import get_llm_config

app = App()

# Inicializar LLMService con la configuración
llm_service = LLMService(config=get_llm_config())

# Paso 1: Refinamiento de la Historia de Usuario
def refine_user_story(user_story):
    return llm_service.refine_story(user_story)

step1 = Step(
    name="Refinamiento de Historia de Usuario",
    components=[
        TextOutput(label="Historia Refinada", function=refine_user_story, input_keys=["user_story"])
    ]
)

# Paso 2: Identificación de Casos Esquina
def identify_corner_cases(refined_story):
    return llm_service.identify_corner_cases(refined_story)

step2 = Step(
    name="Identificación de Casos Esquina",
    components=[
        TextOutput(label="Casos Esquina Identificados", function=identify_corner_cases, input_keys=["refined_story"])
    ]
)

# Paso 3: Estrategia de Testing
async def propose_testing_strategy(refined_story, corner_cases):
    testing_strategy = await llm_service.propose_testing_strategy(refined_story, corner_cases)
    return testing_strategy

step3 = Step(
    name="Estrategia de Testing",
    components=[
        TextOutput(label="Estrategias de Testing Recomendadas", function=propose_testing_strategy, input_keys=["refined_story", "corner_cases"]),
        Confirmation(label="¿Estás de acuerdo con las estrategias de testing propuestas?", key="confirm_testing_strategy")
    ],
    condition=lambda data: data["confirm_testing_strategy"],
    final=True
)

# Agregar pasos al flujo
app.add_steps([step1, step2, step3])

if __name__ == "__main__":
    app.run()

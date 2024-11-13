from langflow import LangFlow, Step
from langflow.steps import TextInput, TextOutput, Confirmation

app = LangFlow(title="Asistente de Refinamiento de Historias de Usuario")

# Paso 1: Mejora de Definición
def refine_definition(user_story):
    # Lógica para refinar la historia de usuario utilizando el modelo LLM
    refined_story = llm_service.refine_story(user_story)
    return refined_story

step1 = Step(
    name="Mejora de Definición",
    components=[
        TextInput(label="Introduce tu historia de usuario", key="user_story"),
        TextOutput(label="Historia Refinada", function=refine_definition, input_key="user_story"),
        Confirmation(label="¿Estás de acuerdo con la historia refinada?", key="confirm_refine")
    ],
    next_step="Identificación de Casos Esquinas",
    condition=lambda data: data["confirm_refine"]
)

# Paso 2: Identificación de Casos Esquinas
def identify_corner_cases(refined_story):
    # Lógica para identificar casos esquinas
    corner_cases = llm_service.identify_corner_cases(refined_story)
    return corner_cases

step2 = Step(
    name="Identificación de Casos Esquinas",
    components=[
        TextOutput(label="Casos Esquinas Identificados", function=identify_corner_cases, input_key="user_story"),
        Confirmation(label="¿Estás de acuerdo con los casos esquinas identificados?", key="confirm_corner_cases")
    ],
    next_step="Estrategia de Testing",
    condition=lambda data: data["confirm_corner_cases"]
)

# Paso 3: Estrategia de Testing
def propose_testing_strategy(refined_story, corner_cases):
    # Lógica para proponer estrategias de testing
    testing_strategy = llm_service.propose_testing_strategy(refined_story, corner_cases)
    return testing_strategy

step3 = Step(
    name="Estrategia de Testing",
    components=[
        TextOutput(label="Estrategias de Testing Recomendadas", function=propose_testing_strategy, input_keys=["user_story", "corner_cases"]),
        Confirmation(label="¿Estás de acuerdo con las estrategias de testing propuestas?", key="confirm_testing_strategy")
    ],
    condition=lambda data: data["confirm_testing_strategy"],
    final=True
)

# Agregar pasos al flujo
app.add_steps([step1, step2, step3])

if __name__ == "__main__":
    app.run()

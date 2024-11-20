import pytest

@pytest.mark.asyncio
async def test_propose_testing_strategy_without_feedback(llm_service):
    """Test para proponer estrategias de testing sin feedback"""
    session_id = llm_service.create_session()
    refined_story = "Como usuario quiero..."
    corner_cases = [
        "1. Caso esquina 1",
        "2. Caso esquina 2"
    ]

    result = await llm_service.propose_testing_strategy(
        session_id=session_id,
        refined_story=refined_story,
        corner_cases=corner_cases
    )

    # Verificar que se recibió un diccionario con las claves esperadas
    assert isinstance(result, dict), "El resultado debe ser un diccionario"
    assert 'testing_strategies' in result, "El resultado debe contener 'testing_strategies'"
    assert 'testing_feedback' in result, "El resultado debe contener 'testing_feedback'"

    # Verificar que las estrategias son una lista no vacía
    testing_strategies = result['testing_strategies']
    assert isinstance(testing_strategies, list), "Las estrategias de testing deben ser una lista"
    assert len(testing_strategies) > 0, "Debe haber al menos una estrategia de testing propuesta"

    # Verificar que el feedback es una cadena no vacía
    testing_feedback = result['testing_feedback']
    assert isinstance(testing_feedback, str), "El feedback debe ser una cadena"
    assert len(testing_feedback.strip()) > 0, "El feedback no debe estar vacío"

@pytest.mark.asyncio
async def test_propose_testing_strategy_with_feedback(llm_service):
    """Test para proponer estrategias de testing con feedback"""
    session_id = llm_service.create_session()
    refined_story = "Como usuario quiero..."
    corner_cases = [
        "1. Caso esquina 1",
        "2. Caso esquina 2"
    ]
    feedback = "Incluir pruebas de estrés y seguridad avanzada"

    result = await llm_service.propose_testing_strategy(
        session_id=session_id,
        refined_story=refined_story,
        corner_cases=corner_cases,
        feedback=feedback
    )

    # Verificar que se recibió un diccionario con las claves esperadas
    assert isinstance(result, dict), "El resultado debe ser un diccionario"
    assert 'testing_strategies' in result, "El resultado debe contener 'testing_strategies'"
    assert 'testing_feedback' in result, "El resultado debe contener 'testing_feedback'"

    # Verificar que las estrategias son una lista no vacía
    testing_strategies = result['testing_strategies']
    assert isinstance(testing_strategies, list), "Las estrategias de testing deben ser una lista"
    assert len(testing_strategies) > 0, "Debe haber al menos una estrategia de testing propuesta"

    # Verificar que el feedback es una cadena no vacía y contiene referencias al feedback proporcionado
    testing_feedback = result['testing_feedback']
    assert isinstance(testing_feedback, str), "El feedback debe ser una cadena"
    assert len(testing_feedback.strip()) > 0, "El feedback no debe estar vacío"
    assert any(keyword in testing_feedback.lower() for keyword in ["pruebas de estrés", "seguridad avanzada"]), \
        "El feedback debe mencionar los cambios relacionados con el feedback proporcionado"

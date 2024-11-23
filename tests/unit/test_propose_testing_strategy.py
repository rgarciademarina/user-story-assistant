import pytest
from uuid import UUID

@pytest.mark.asyncio
async def test_propose_testing_strategy_without_feedback(mock_llm_service):
    """Test para proponer estrategia de pruebas sin feedback"""
    session_id = mock_llm_service.create_session()
    refined_story = "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal"
    corner_cases = [
        "1. **Intentos de Inicio de Sesión Fallidos:** El usuario ingresa una contraseña incorrecta repetidamente.",
        "2. **Acceso desde Ubicaciones No Reconocidas:** Intentos de inicio de sesión desde ubicaciones geográficas inusuales."
    ]

    result = await mock_llm_service.propose_testing_strategy(
        session_id=session_id,
        refined_story=refined_story,
        corner_cases=corner_cases
    )

    assert isinstance(result, dict)
    assert 'testing_strategies' in result
    assert 'testing_feedback' in result

    strategies = result['testing_strategies']
    assert isinstance(strategies, list)
    assert len(strategies) > 0

    feedback = result['testing_feedback']
    assert isinstance(feedback, str)
    assert len(feedback.strip()) > 0

@pytest.mark.asyncio
async def test_propose_testing_strategy_with_feedback(mock_llm_service):
    """Test para proponer estrategia de pruebas con feedback"""
    session_id = mock_llm_service.create_session()
    refined_story = "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal"
    corner_cases = [
        "1. **Intentos de Inicio de Sesión Fallidos:** El usuario ingresa una contraseña incorrecta repetidamente.",
        "2. **Acceso desde Ubicaciones No Reconocidas:** Intentos de inicio de sesión desde ubicaciones geográficas inusuales."
    ]
    feedback = "Incluir pruebas de integración con el sistema de autenticación"

    result = await mock_llm_service.propose_testing_strategy(
        session_id=session_id,
        refined_story=refined_story,
        corner_cases=corner_cases,
        feedback=feedback
    )

    assert isinstance(result, dict)
    assert 'testing_strategies' in result
    assert 'testing_feedback' in result

    strategies = result['testing_strategies']
    assert isinstance(strategies, list)
    assert len(strategies) > 0

    # Verificar que el feedback se incorporó
    strategies_text = ' '.join(strategies).lower()
    assert 'integración' in strategies_text or 'autenticación' in strategies_text

    feedback = result['testing_feedback']
    assert isinstance(feedback, str)
    assert len(feedback.strip()) > 0

@pytest.mark.asyncio
async def test_propose_testing_strategy_with_existing_strategies(mock_llm_service):
    """Test para proponer estrategia de pruebas con estrategias existentes"""
    session_id = mock_llm_service.create_session()
    refined_story = "Como usuario quiero poder iniciar sesión para acceder a mi cuenta personal"
    corner_cases = [
        "1. **Intentos de Inicio de Sesión Fallidos:** El usuario ingresa una contraseña incorrecta repetidamente.",
        "2. **Acceso desde Ubicaciones No Reconocidas:** Intentos de inicio de sesión desde ubicaciones geográficas inusuales."
    ]
    existing_testing_strategies = [
        "1. **Test de Credenciales Válidas:** Verificar inicio de sesión exitoso con credenciales correctas.",
        "2. **Test de Bloqueo de Cuenta:** Verificar que la cuenta se bloquea después de múltiples intentos fallidos."
    ]
    feedback = "Agregar pruebas de rendimiento"

    result = await mock_llm_service.propose_testing_strategy(
        session_id=session_id,
        refined_story=refined_story,
        corner_cases=corner_cases,
        feedback=feedback,
        existing_testing_strategies=existing_testing_strategies
    )

    assert isinstance(result, dict)
    assert 'testing_strategies' in result
    assert 'testing_feedback' in result

    strategies = result['testing_strategies']
    assert isinstance(strategies, list)
    assert len(strategies) > 0

    # Verificar que los conceptos clave de las estrategias existentes están cubiertos
    strategies_text = ' '.join(strategies).lower()

    key_concepts = {
        'credenciales': ['credencial', 'contraseña', 'usuario'],
        'autenticación': ['autenticar', 'acceso', 'iniciar sesión'],
        'seguridad': ['seguro', 'protección', 'vulnerabilidad'],
        'rendimiento': ['rendimiento', 'performance', 'carga']
    }

    for concept, alternatives in key_concepts.items():
        assert any(alt in strategies_text for alt in alternatives), \
            f"Concepto '{concept}' o sus alternativas {alternatives} no encontrados en las estrategias"

    feedback = result['testing_feedback']
    assert isinstance(feedback, str)
    assert len(feedback.strip()) > 0